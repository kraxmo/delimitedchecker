#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@purpose: This script checks for embedded pipe characters within pipe-delimited file 
          where header count != detail count and writes bad records to output file
@author : Jim Kraxberger
@created: 2021-11-16
@updated: 2024-11-01
@command: (UNIX)    python delimitedfilechecker.py --delimiter '|' --filename 'filename' -v
          (Windows) python delimitedfilechecker.py --delimiter "|" --filename "filename" -v
"""

import argparse as ap
import csv
from datetime import datetime

HELP_EPILOG = '''

The purpose of this script is to check file delimiter count mismatches (header vs. detail)

Output file (if invalid) contains header and identified invalid records

'''

class BadRecord:
    """Defines bad record with incorrect number of delimiters"""
    def __init__(self, key, value):  # class constructor
        self.key = key               # contains field count
        self.value = value           # contains record

    def __iter__(self):              # allows object to iterate within loop
        yield self

class ParseDelimitedFile():
    r"""
        A class that parses passed filename by delimiter to verify header record delimiter counts
        match each detail record
        
        :Example:
        >>> pdf = ParseDelimitedFile(',', r'C:\myfile.csv')
    """
    ERROR_DELIMITER_FILE_SUFFIX = '.ERROR_DELIMITER'
    
    def __init__(self, delimiter, filename, verbose) -> None:
        self.delimiter   = delimiter
        self.filename    = filename
        self.verbose     = verbose
        self.badrecords  = []
    
    def parse(self) -> bool:
        """
        Reads passed delimiter and compares delimiter count of header record (first record) to each detail record
        
        :return: Returns True if valid run else raises ValueError
        :rtype: bool
        """
        FILESUFFIX = '_' + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + self.ERROR_DELIMITER_FILE_SUFFIX
        dict_tally = {}
        record_count = 0
        for record in self.read_delimited_record(self.filename):
            record_count += 1
            if record_count == 1:
                headerDelimiterCount = record.count(self.delimiter)                 # get header delimiter count
                self.save_bad_record(record, record_count, headerDelimiterCount)    # append record#, fieldcount, header record to BadRecord list
                continue

            if len(record.strip()) > 0:                             # if any detail data exists
                detailDelimiterCount = record.count(self.delimiter) # get detail delimiter count
                if headerDelimiterCount != detailDelimiterCount:    # if header count <> detail, save record
                    self.save_bad_record(record, record_count, detailDelimiterCount)

                # capture delimiter length statistics                    
                try:
                    dict_tally[detailDelimiterCount] += 1
                except KeyError:
                    dict_tally[detailDelimiterCount] = 1

        summary = '|'.join([f"{k}: {dict_tally[k]}" for k in dict_tally])
        if (total_bad_records := len(self.badrecords) - 1):     # write output file to include filename, delimiter, expected fields and all bad records record#, fieldcount, record (including header)
            message = 'filename :' + self.filename + '\ndelimiter:' + self.delimiter + '\nfields   :' + '{:0>.4f}'.format(headerDelimiterCount / 10000)[-4:] + '\n\nDelimiter Count Summary:\n' + '\n'.join(summary.split('|')) + '\n\nDelimiter Header and Bad Record Detail:\n' + '\n'.join(bad.key + ':' + ''.join(bad.value) for bad in self.badrecords)
            with open(self.filename + FILESUFFIX, 'w') as badfile:
                badfile.write(message)

            if self.verbose:
                print('- CSV Status: BAD')
                print('  + Delimiter Summary Record Count: (total delimiters: records)')
                print('    * ' + str(headerDelimiterCount) + ': 1 (header)')
                print('    * ' + '\n    * '.join(summary.split('|')))
            
            # Format and raise error condition   
            message = f"File {self.filename} has {total_bad_records} badly delimited record{'s' if total_bad_records > 1 else ''}"
            print(f"{message}\nSee file {self.filename + FILESUFFIX} for details\n")
            raise ValueError(message)
        else: 
            if self.verbose: print('- CSV Status: GOOD')
        
        return True

    def read_delimited_record(self, filename: str):
        """
        Reads each record from passed filename using a generator pattern
        
        :returns: record (generator object)
        :rtype: str
        """
        try:
            with open(filename, "r", encoding='utf-8') as csvfile:  # open filename with file handle
                ctr = 0
                for record in csv.reader(csvfile, delimiter=self.delimiter):
                    if self.verbose: 
                        ctr += 1
                        print(f"  + {ctr}: {record[0:50]}")
                        
                    yield self.delimiter.join(record)
                    
        except UnicodeDecodeError as err:
            message = f"\nRecord: {ctr}\nError: {err}"
            print(message)
            raise err
            
    def save_bad_record(self, record: str, record_count: int, delimiter_count: int) -> None:
        """append record#, fieldcount, header record to BadRecord list"""
        self.badrecords.append(BadRecord('{:0>14.4f}'.format(record_count + delimiter_count/10000), record))

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
        description='Check file delimiter counts to verify detail vs. header',
        epilog=HELP_EPILOG,
        formatter_class=ap.RawDescriptionHelpFormatter,
    )
    parser.add_argument('delimiter', type=str, default=",", help='Input file CSV delimiter')
    parser.add_argument('filename', type=str, help='Input filename')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode: True = print process messages, False(default) = omit process messages')
    return parser.parse_args()

DEBUG = False
if __name__ == '__main__':
    if DEBUG:
        delimiter = ','
        filename = r'.\data\badfile.csv'
        verbose = True
    else:
        args = get_args()
        delimiter = args.delimiter
        filename = args.filename
        verbose = args.verbose
        if args.verbose:
            print(f'\ndelimitedfilechecker:\n- delimiter: {args.delimiter}\n- filename : {args.filename}\n- verbose  : {args.verbose}')

    pdf = ParseDelimitedFile(delimiter, filename, verbose)
    pdf.parse()
