import delimitedfilechecker as dfc1
from os import path
import sys
import unittest

class TestDelimitedFileChecker(unittest.TestCase):
    VERBOSE = False
    def identify(func):
        def wrapper(*args, **kwargs):
            if TestDelimitedFileChecker.VERBOSE: print(f"\nTEST: {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    
    def setUp(self):
        self.delimiter = "|"
        self.directory   = path.dirname(path.realpath(sys.argv[0]))+'/data'
        self.goodfile    = "goodfile.csv"
        self.badfile     = "badfile.csv"
        
    @identify
    def test_good_file(self):
        self.filename = path.join(self.directory, self.goodfile)
        pdf = dfc1.ParseDelimitedFile(self.delimiter, self.filename, self.VERBOSE)
        self.assertTrue(pdf.parse())

    @identify
    def test_bad_file_1(self):
        self.filename = path.join(self.directory, self.badfile)
        pdf = dfc1.ParseDelimitedFile(self.delimiter, self.filename, self.VERBOSE)
        self.assertRaises(ValueError)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '-v':   
        TestDelimitedFileChecker.VERBOSE = True
    else:
        TestDelimitedFileChecker.VERBOSE = False
        
    unittest.main()