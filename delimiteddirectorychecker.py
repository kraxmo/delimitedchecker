#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@purpose: This script reads through supplied directory and calls delimitedfilechecker.py with each directory file and provided delimiter
@author : Jim Kraxberger
@created: 2022-08-19
@command: (UNIX)     python delimiteddirectorychecker.py '|' 'directory'
          (Windowns) python delimiteddirectorychecker.py "|" "directory"
"""

import argparse as ap
import delimitedfilechecker as dfc
import os
import sys

HELP_EPILOG = '''

The purpose of this script is to check all files in specified directory for delimiter counts mismatches (header vs. detail)

'''

def get_args():
    parser = ap.ArgumentParser(
        description='Check file delimiter counts to verify detail vs. header',
        epilog=HELP_EPILOG,
        formatter_class=ap.RawDescriptionHelpFormatter,
    )
    parser.add_argument('delimiter', required=True, default=",", help='Input file CSV delimiter')
    parser.add_argument('directory', required=True, help='Input directory')
    parser.add_argument('-v', '--verbosemode', action='store_true', help='Verbose mode: True = print process messages, False(default) = omit process messages')
    return parser.parse_args()

def ReadDirFiles(directory):
    for file in os.listdir(directory):
        yield file

if __name__ == '__main__':
    args = get_args()
    if args.verbosemode:
        print('\n' + '=' * 50)
        print(f'delimitedfilechecker\n- delimiter  : {args.delimiter}\n- directory  : {args.directory}\n- verbosemode: {args.verbosemode}')
        print('=' * 50 + '\n')

    errorCount = 0
    delimiter = args.delimiter
    directory = args.directory
    verbose   = args.verbosemode
    for file in ReadDirFiles(args.directory):
        if file.endswith(".csv"):
            filespec = directory + "\\" + file
            try:
                d = dfc.ParseDelimitedFile(delimiter, file, verbose)
                if verbose: print(f"{'-' * 50}\nFILENAME: '{filespec}'")
                d.parse() # call function passing delimiter and filename
            except:
                errorCount += 1
            finally:
                if verbose: print('-' * 50 + '\n')
    
    if errorCount:
        print(f"Directory {directory} has {str(errorCount)} badly delimited file{'s' if errorCount > 1 else ''}")
        if not verbose: print('- See directory files with suffix _ERROR_DELIMITER_YYYY_MM_DD_HH_MM_DD for details')

"""
# Immediate file run
delimiter = "|"
errorCount = 0
dir = "."
for file in ReadDirFiles(dir):
    if file.endswith(".csv"):
        filespec = dir+"\\"+file
        print(f"\nCHECKING: {filespec}\n")
        try:
            d = dfc.ParseDelimitedFile(delimiter, file, True)
            d.parse() # call function passing delimiter and filename
            print('- SUCCESS')
        except:
            errorCount += 1
            print('- ERROR')

if errorCount > 0:
    print(f"Directory {dir} has {str(errorCount)} badly delimited file{'s' if errorCount > 1 else ''}. See directory files with suffix _ERROR_DELIMITER_YYYY_MM_DD_HH_MM_DD for details")
"""