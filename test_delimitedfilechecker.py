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
        self.goodnestedfile = "goodnested.csv"
        self.badnestedfile = "badnested.csv"

    @identify
    def test_good_file_with_outputfile(self):
        good_content = "col1,col2,col3\nval1,val2,val3\nval4,val5,val6"

        def open_side_effect(file, mode="r", encoding=None, *args, **kwargs):
            fname = str(file)
            if fname.endswith(self.goodfile) and "r" in mode:
                return io.StringIO(good_content)
            if "w" in mode and fname.endswith(
                dfc1.ParseDelimitedFile.ERROR_DELIMITER_FILE_SUFFIX
            ):
                return _StdoutWriter()
            return _original_open(file, mode, encoding=encoding, *args, **kwargs)

        with patch("builtins.open", side_effect=open_side_effect):
            self.filename = path.join(self.directory, self.goodfile)
            pdf = dfc1.ParseDelimitedFile(self.delimiter, self.filename, True)
            self.assertTrue(pdf.parse_records())

    @identify
    def test_good_file_without_outputfile(self):
        good_content = "col1,col2,col3\nval1,val2,val3\nval4,val5,val6"

        def open_side_effect(file, mode="r", encoding=None, *args, **kwargs):
            fname = str(file)
            if fname.endswith(self.goodfile) and "r" in mode:
                return io.StringIO(good_content)
            if "w" in mode and fname.endswith(
                dfc1.ParseDelimitedFile.ERROR_DELIMITER_FILE_SUFFIX
            ):
                return _StdoutWriter()
            return _original_open(file, mode, encoding=encoding, *args, **kwargs)

        with patch("builtins.open", side_effect=open_side_effect):
            self.filename = path.join(self.directory, self.goodfile)
            pdf = dfc1.ParseDelimitedFile(self.delimiter, self.filename, False)
            self.assertTrue(pdf.parse_records())

    @identify
    def test_bad_file_with_outputfile(self):
        bad_content = "col1,col2,col3\nval1,val2\nonlyonefield\nval4,val5\nval6"

        def open_side_effect(file, mode="r", encoding=None, *args, **kwargs):
            fname = str(file)
            if fname.endswith(self.badfile) and "r" in mode:
                return io.StringIO(bad_content)
            if "w" in mode and fname.endswith(
                dfc1.ParseDelimitedFile.ERROR_DELIMITER_FILE_SUFFIX
            ):
                return _StdoutWriter()
            return _original_open(file, mode, encoding=encoding, *args, **kwargs)

        with patch("builtins.open", side_effect=open_side_effect):
            filename = path.join(self.directory, self.badfile)
            pdf = dfc1.ParseDelimitedFile(self.delimiter, filename, True)
            self.assertFalse(pdf.parse_records())

    @identify
    def test_bad_file_without_outputfile(self):
        bad_content = "col1,col2,col3\nval1,val2\nonlyonefield\nval4,val5\nval6"

        def open_side_effect(file, mode="r", encoding=None, *args, **kwargs):
            fname = str(file)
            if fname.endswith(self.badfile) and "r" in mode:
                return io.StringIO(bad_content)
            if "w" in mode and fname.endswith(
                dfc1.ParseDelimitedFile.ERROR_DELIMITER_FILE_SUFFIX
            ):
                return _StdoutWriter()
            return _original_open(file, mode, encoding=encoding, *args, **kwargs)

        with patch("builtins.open", side_effect=open_side_effect):
            filename = path.join(self.directory, self.badfile)
            pdf = dfc1.ParseDelimitedFile(self.delimiter, filename, False)
            self.assertFalse(pdf.parse_records())

    @identify
    def test_good_nested_delimiters_in_quoted_field(self):
        nested_content = (
            'col1,col2,col3\n"a,with,commas",val2,val3\nval4,"val,with,comma",val6'
        )

        def open_side_effect(file, mode="r", encoding=None, *args, **kwargs):
            fname = str(file)
            if fname.endswith(self.goodnestedfile) and "r" in mode:
                return io.StringIO(nested_content)
            if "w" in mode and fname.endswith(
                dfc1.ParseDelimitedFile.ERROR_DELIMITER_FILE_SUFFIX
            ):
                return _StdoutWriter()
            return _original_open(file, mode, encoding=encoding, *args, **kwargs)

        with patch("builtins.open", side_effect=open_side_effect):
            filename = path.join(self.directory, self.goodnestedfile)
            pdf = dfc1.ParseDelimitedFile(self.delimiter, filename, True)
            self.assertTrue(pdf.parse_records())

    @identify
    def test_bad_nested_delimiters_in_quoted_field(self):
        nested_content = (
            'col1,col2,col3\n"a,with,commas",val2,val3\nval4,"val,with,comma",,val6'
        )

        def open_side_effect(file, mode="r", encoding=None, *args, **kwargs):
            fname = str(file)
            if fname.endswith(self.badnestedfile) and "r" in mode:
                return io.StringIO(nested_content)
            if "w" in mode and fname.endswith(
                dfc1.ParseDelimitedFile.ERROR_DELIMITER_FILE_SUFFIX
            ):
                return _StdoutWriter()
            return _original_open(file, mode, encoding=encoding, *args, **kwargs)

        with patch("builtins.open", side_effect=open_side_effect):
            filename = path.join(self.directory, self.badnestedfile)
            pdf = dfc1.ParseDelimitedFile(self.delimiter, filename, True)
            self.assertFalse(pdf.parse_records())


if __name__ == "__main__":
    unittest.main()
