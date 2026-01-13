import delimitedfilechecker as dfc1
from os import path
import sys
import unittest
import io
import builtins as _builtins
from unittest.mock import patch

# preserve original open for fallthrough in mocks
_original_open = _builtins.open


class _StdoutWriter:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def write(self, s):
        sys.stdout.write(s)

    def flush(self):
        sys.stdout.flush()


def identify(func):
    def wrapper(*args, **kwargs):
        if TestDelimitedFileChecker.VERBOSE:
            print(f"\nTEST: {func.__name__}")
        return func(*args, **kwargs)

    return wrapper


class TestDelimitedFileChecker(unittest.TestCase):
    VERBOSE = True

    def setUp(self):
        self.delimiter = ","
        self.directory = path.dirname(path.realpath(sys.argv[0])) + "/data"
        self.goodfile = "goodfile.csv"
        self.badfile = "badfile.csv"

    @identify
    def test_good_file(self):
        # Provide CSV content where header and detail delimiter counts match
        good_content = "col1,col2\nval1,val2\nval3,val4\n"

        def open_side_effect(file, mode="r", encoding=None, *args, **kwargs):
            fname = str(file)
            # read the mocked good file
            if fname.endswith(self.goodfile) and "r" in mode:
                return io.StringIO(good_content)
            # reroute any ERROR_DELIMITER write output to stdout
            if "w" in mode and fname.endswith(
                dfc1.ParseDelimitedFile.ERROR_DELIMITER_FILE_SUFFIX
            ):
                return _StdoutWriter()
            return _original_open(file, mode, encoding=encoding, *args, **kwargs)

        with patch("builtins.open", side_effect=open_side_effect):
            self.filename = path.join(self.directory, self.goodfile)
            pdf = dfc1.ParseDelimitedFile(self.delimiter, self.filename)
            with self.assertRaises(SystemExit) as cm:
                pdf.parse()

        self.assertEqual(cm.exception.code, 0)

    @identify
    def test_bad_file(self):
        # Provide CSV content where a detail row has different delimiter count
        bad_content = "col1,col2\nval1,val2\nonlyonefield\n"

        def open_side_effect(file, mode="r", encoding=None, *args, **kwargs):
            fname = str(file)
            # read the mocked bad file
            if fname.endswith(self.badfile) and "r" in mode:
                return io.StringIO(bad_content)
            # reroute any ERROR_DELIMITER write output to stdout
            if "w" in mode and fname.endswith(
                dfc1.ParseDelimitedFile.ERROR_DELIMITER_FILE_SUFFIX
            ):
                return _StdoutWriter()
            return _original_open(file, mode, encoding=encoding, *args, **kwargs)

        with patch("builtins.open", side_effect=open_side_effect):
            filename = path.join(self.directory, self.badfile)
            pdf = dfc1.ParseDelimitedFile(self.delimiter, filename)
            with self.assertRaises(SystemExit) as cm:
                pdf.parse()

        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
