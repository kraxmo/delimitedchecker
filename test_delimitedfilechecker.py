import delimitedfilechecker as dfc1
import unittest

class TestDelimitedFileChecker(unittest.TestCase):
    def setUp(self):
        self.delimiter = "|"
        self.verbosemode = False
        
    def test_good_file(self):
        self.filename = "goodfile.csv"
        pdf = dfc1.ParseDelimitedFile(self.delimiter, self.filename, self.verbosemode)
        self.assertTrue(pdf.parse())

    def test_bad_file_1(self):
        self.filename = "badfile.csv"
        pdf = dfc1.ParseDelimitedFile(self.delimiter, self.filename, self.verbosemode)
        self.assertRaises(ValueError, pdf.parse)

    def test_bad_file_2(self):
        self.filename = "badfile.csv"
        pdf = dfc1.ParseDelimitedFile(self.delimiter, self.filename, self.verbosemode)
        with self.assertRaises(ValueError) as cm:
            pdf.parse()

        cm.exception
        message = cm.exception.args[0]
        self.assertTrue(message.startswith('File badfile.csv has 3 badly delimited records'))
    
    def test_bad_file_3(self):
        self.filename = "badfile.csv"
        pdf = dfc1.ParseDelimitedFile(self.delimiter, self.filename, self.verbosemode)
        self.assertRaisesRegex(ValueError, r'File badfile.csv has 3 badly delimited records', pdf.parse)
