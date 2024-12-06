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
from datetime import datetime

HELP_EPILOG = '''

The purpose of this script is to check file delimiter count mismatches (header vs. detail)

Output file (if invalid) contains header and identified invalid records

'''

def get_args():
    parser = ap.ArgumentParser(
        description='Check file delimiter counts to verify detail vs. header',
        epilog=HELP_EPILOG,
        formatter_class=ap.RawDescriptionHelpFormatter,
    )
    parser.add_argument('delimiter', type=str, default=",", help='Input file CSV delimiter')
    parser.add_argument('filename', type=str, help='Input filename')
    parser.add_argument('-v', '--verbosemode', action='store_true', help='Verbose mode: True = print process messages, False(default) = omit process messages')
    return parser.parse_args()

class BadRecord:
    """Defines bad record with incorrect number of delimiters"""
    def __init__(self, key, value):  # class constructor
        self.key = key               # contains field count
        self.value = value           # contains record
    def __iter__(self):              # allows object to iterate within loop
        yield self

class ParseDelimitedFile():
    def __init__(self, delimiter, filename, verbosemode):
        self.delimiter   = delimiter
        self.filename    = filename
        self.verbosemode = verbosemode
        self.badrecords  = []
    
    def parse(self):
        """Reads passed delimiter and compares delimiter count of header record (first record) to each detail record"""
        FILESUFFIX = '_' + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.ERROR_DELIMITER'
        dict_tally = {}
        record_count = 0
        for record in self.read_delimited_record(self.filename):
            record_count += 1
            if record_count == 1:
                # get header delimiter count
                headerDelimiterCount = record.count(self.delimiter)
                # append record#, fieldcount, header record to BadRecord list
                self.save_bad_record(record, record_count, headerDelimiterCount)
                continue

            # if any detail data exists
            if len(record.strip()) > 0:                             
                detailDelimiterCount = record.count(self.delimiter) # get detail delimiter count
                if headerDelimiterCount != detailDelimiterCount: # if header count <> detail, save record
                    self.save_bad_record(record, record_count, detailDelimiterCount)

                # capture delimiter length statistics                    
                try:
                    dict_tally[detailDelimiterCount] += 1
                except KeyError:
                    dict_tally[detailDelimiterCount] = 1

        # count total bad records
        totalDelimiterCount = len(self.badrecords) - 1
        summary = '|'.join([f"{k}: {dict_tally[k]}" for k in dict_tally])
        
        if totalDelimiterCount:
            # write output file to include filename, delimiter, expected fields and all bad records record#, fieldcount, record (including header)
            message = 'filename :' + self.filename + '\ndelimiter:' + self.delimiter + '\nfields   :' + '{:0>.4f}'.format(headerDelimiterCount / 10000)[-4:] + '\n\nDelimiter Count Summary:\n' + summary + '\n' + ''.join(bad.key + ':' + ''.join(bad.value) for bad in self.badrecords)
            with open(self.filename + FILESUFFIX, 'w') as badfile:
                badfile.write(message)

            if self.verbosemode:
                print('- CSV Status: BAD')
                print('  + Delimiter Summary Record Count: (total delimiters: records)')
                print('    * ' + str(headerDelimiterCount) + ': 1 (header)')
                print('    * ' + '\n    * '.join(summary.split('|')))
            
            # Format and raise error condition   
            errorMessage = 'File ' + self.filename + ' has ' + str(totalDelimiterCount) + ' badly delimited record' + ('s' if totalDelimiterCount > 1 else '')
            raise ValueError(errorMessage)
        else: 
            if self.verbosemode: print('- CSV Status: GOOD')
        
        return True

    def read_delimited_record(self, filename):
        """Read each record from passed filename using a generator pattern"""
        with open(filename, "r") as csvfile: # open filename with file handle
            for rec in csvfile:
                yield rec

    def save_bad_record(self, record, record_count, delimiter_count):
        """append record#, fieldcount, header record to BadRecord list"""
        self.badrecords.append(BadRecord('{:0>14.4f}'.format(record_count + delimiter_count/10000), record))

# Command-line run
if __name__ == '__main__':
    args = get_args()
    if args.verbosemode:
        print(f'delimitedfilechecker:\n- delimiter: {args.delimiter}\n- filename: {args.filename}\n- verbosemode: {args.verbosemode}')
        
    pdf = ParseDelimitedFile(args.delimiter, args.filename, args.verbosemode)
    pdf.parse()
