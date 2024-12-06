#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@purpose: This script reads through supplied directory and calls delimitedfilechecker.py with each directory file and provided delimiter
@author : Jim Kraxberger
@created: 2022-08-19
@command: (UNIX)     python delimiteddirectorychecker.py '|' 'directory' 'csv'
          (Windowns) python delimiteddirectorychecker.py "|" "directory" "csv"
"""

import argparse as ap
import delimitedfilechecker as dfc
import os

DEBUG = False
HELP_EPILOG = '''

The purpose of this script is to check all files in specified directory for delimiter counts mismatches (header vs. detail)

'''

class ParseDelimitedDirectory:
    def __init__(self, delimiter: str, directory: str, filesuffix: str, verbosemode: bool):
        self.delimiter   = delimiter
        self.directory   = os.path.normpath(directory)
        self.filesuffix  = filesuffix
        if self.filesuffix:
            self.filesuffix = '.'+filesuffix
            
        self.verbosemode = verbosemode

    def parse(self):
        """
        Reads passed directory's files and calls delimitedfilechecker with delimiter and file
        """

        if self.verbosemode:
            print('\n' + '=' * 50)
            print(f'delimitedfilechecker\n- delimiter  : {self.delimiter}\n- directory  : {self.directory}\n- filesuffix     : {self.filesuffix}\n- verbosemode: {self.verbosemode}')
            print('=' * 50 + '\n')

        if not os.path.exists(self.directory):
            print(f"Error: directory '{self.directory} does not exist.")
            return
        
        if not os.path.isdir(self.directory):
            print(f"Error: path '{self.directory} is not a directory.")

        errorCount = 0
        if self.verbosemode: print(f"DIRECTORY: {self.directory}")
        for file in self.read_directory_files():
            try:
                d = dfc.ParseDelimitedFile(self.delimiter, file, self.verbosemode)
                if self.verbosemode: print(f"{'-' * 50}\nFILENAME: '{file}'")
                d.parse() # call function passing delimiter and filename
            except Exception as e:
                print(f"Exception: {e}")
                errorCount += 1
            finally:
                if self.verbosemode: print('-' * 50 + '\n')
        
        if errorCount:
            print(f"Directory {self.directory} has {str(errorCount)} badly delimited file{'s' if errorCount > 1 else ''}")
            if not self.verbosemode: print('- See directory files with filesuffix _ERROR_DELIMITER_YYYY_MM_DD_HH_MM_DD for details')

    def read_directory_files(self):
        """
        Reads each file in directory whose suffix matches specified filesuffix and is not an error file
        
        :returns: file (generator object)
        :rtype: str
        """
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith(self.filesuffix) and not file.endswith(dfc.ParseDelimitedFile.ERROR_DELIMITER_FILE_SUFFIX):
                    file_path = os.path.join(root, file)
                    yield file_path

def get_args():
    """
    Reads, validates, and returns command line arguments
    
    :Example:
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--foo')
    _StoreAction(option_strings=['--foo'], dest='foo', nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None)
    >>> args = parser.parse_args(['--foo', 'BAR'])
    >>> vars(args)
    {'foo': 'BAR'}
    >>> args.foo
    'BAR'
    
    :return: parsed arguments
    :rtype: object subclass with a readable string representation
    """
    
    parser = ap.ArgumentParser(
        description="Check directory's delimited files' delimiter counts to verify detail vs. header",
        epilog=HELP_EPILOG,
        formatter_class=ap.RawDescriptionHelpFormatter,
    )
    parser.add_argument('delimiter', type=str, default=",", help='Input file CSV delimiter')
    parser.add_argument('directory', type=str, help='Input directory')
    parser.add_argument('-f', '--filesuffix', type=str, default="csv", help="File suffix (default: csv), no suffix = ''")
    parser.add_argument('-v', '--verbosemode', action='store_true', help='Verbose mode: True = print process messages, False(default) = omit process messages')
    return parser.parse_args()

if __name__ == '__main__':
    if DEBUG:
        args = ap.Namespace(delimiter='|', directory='.', filesuffix='csv', verbosemode=True)
    else:
        args = get_args()

    pdd = ParseDelimitedDirectory(args.delimiter, args.directory, args.filesuffix, args.verbosemode)
    pdd.parse()
