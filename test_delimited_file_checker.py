import delimited_file_checker as dfc1
from os import path
import sys
import unittest
import io
import builtins as _builtins
from unittest.mock import patch

# python -m unittest test_async_batch_scanner.py -v

# preserve original open for fallthrough in mocks
_original_open = _builtins.open

BATCH_ID = "test1"


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
            print("\n" + "=" * 70)
            print(f"\n*TEST: {func.__name__}")
        return func(*args, **kwargs)

    return wrapper


class TestDelimitedFileChecker(unittest.TestCase):
    VERBOSE = True

    def setUp(self):
        self.delimiter = ","
        self.directory = path.dirname(path.realpath(sys.argv[0])) + "/data"
        self.goodfile = "goodfile.csv"
        self.badfile = "badfile.csv"
        self.goodnestedfile = "nestedgood.csv"
        self.badnestedfile = "nestedbad.csv"
        self.badunder = "badunder.csv"
        self.badover = "badover.csv"

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
            pdf = dfc1.ParseDelimitedFile(
                self.delimiter, self.filename, True, batch_id=BATCH_ID
            )
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
            pdf = dfc1.ParseDelimitedFile(
                self.delimiter, self.filename, False, batch_id=BATCH_ID
            )
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
            pdf = dfc1.ParseDelimitedFile(
                self.delimiter, filename, True, batch_id=BATCH_ID
            )
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
            pdf = dfc1.ParseDelimitedFile(
                self.delimiter, filename, False, batch_id=BATCH_ID
            )
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
            pdf = dfc1.ParseDelimitedFile(
                self.delimiter, filename, write_output_file=True, batch_id=BATCH_ID
            )
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
            pdf = dfc1.ParseDelimitedFile(
                self.delimiter, filename, True, batch_id=BATCH_ID
            )
            self.assertFalse(pdf.parse_records())

    @identify
    def test_bad_underfile_with_outputfile(self):
        bad_content = "col1,col2,col3\nval1,val2\nval4,val5\nval6"

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
            filename = path.join(self.directory, self.badunder)
            pdf = dfc1.ParseDelimitedFile(
                self.delimiter, filename, True, batch_id=BATCH_ID
            )
            self.assertFalse(pdf.parse_records())

    @identify
    def test_bad_overfile_with_outputfile_error(self):
        bad_content = "col1,col2,col3\nval1,val2,val3\nval4,val5\nval6\nval7"

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
            filename = path.join(self.directory, self.badover)
            pdf = dfc1.ParseDelimitedFile(
                self.delimiter, filename, True, batch_id=BATCH_ID
            )
            self.assertFalse(pdf.parse_records())

    @identify
    def test_bad_overfile_with_outputfile_ignore(self):
        bad_content = "col1,col2,col3\nval1,val2,val3\nval4,val5\nval6\nval7"

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
            filename = path.join(self.directory, self.badover)
            pdf = dfc1.ParseDelimitedFile(
                self.delimiter,
                filename,
                True,
                ignore_over_count=True,
                batch_id=BATCH_ID,
            )
            self.assertTrue(pdf.parse_records())

    @identify
    def test_good_wrong_file_with_outputfile(self):
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
            pdf = dfc1.ParseDelimitedFile(
                self.delimiter,
                self.filename,
                True,
                ignore_over_count=False,
                expected_delimiter_count=3,
                batch_id=BATCH_ID,
            )
            self.assertFalse(pdf.parse_records())

    @identify
    def test_replacement_delimiter_writes_fixed_file(self):
        # header + two rows
        content = "col1,col2,col3\nval1,val2,val3\nval4,val5,val6"
        replacement = "|"
        fixed_capture = {"f": None}

        class FixedWriter:
            def __init__(self):
                self._parts = []

            def write(self, s):
                self._parts.append(s)

            def writelines(self, lines):
                self._parts.extend(lines)

            def flush(self):
                pass

            def close(self):
                pass

            def getvalue(self):
                return "".join(self._parts)


        def open_side_effect(file, mode="r", encoding=None, *args, **kwargs):
            fname = str(file)
            if fname.endswith(self.goodfile) and "r" in mode:
                return io.StringIO(content)
            # capture write to _FIXED file
            if "w" in mode and fname.endswith(self.goodfile + "_FIXED"):
                fixed_capture["f"] = FixedWriter()
                return fixed_capture["f"]
            return _original_open(file, mode, encoding=encoding, *args, **kwargs)

        with patch("builtins.open", side_effect=open_side_effect):
            filename = path.join(self.directory, self.goodfile)
            pdf = dfc1.ParseDelimitedFile(
                self.delimiter,
                filename,
                write_output_file=True,
                batch_id=BATCH_ID,
                replacement_delimiter=replacement,
            )
            # run parse; expect it to return header delimiter count (2)
            self.assertEqual(pdf.parse_records(), 2)

        # verify fixed file was written and contents use replacement delimiter
        self.assertIsNotNone(fixed_capture["f"])
        fixed_value = fixed_capture["f"].getvalue()
        expected = "col1|col2|col3\nval1|val2|val3\nval4|val5|val6\n"
        self.assertEqual(fixed_value, expected)


if __name__ == "__main__":
    unittest.main()
