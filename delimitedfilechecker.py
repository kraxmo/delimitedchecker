#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@purpose: This script checks for embedded pipe characters within pipe-delimited file
          where header count != detail count and writes bad records to output file
@author : Jim Kraxberger
@created: 2021-11-16
@updated: 2026-01-12
@command: (UNIX)    python delimitedfilechecker.py ',' 'filename'
          (Windows) python delimitedfilechecker.py "," "filename"
"""

import argparse as ap
import csv
from datetime import datetime
import logging
import sys
from typing import Iterable

HELP_EPILOG = """

The purpose of this script is to check file delimiter count mismatches (header vs. detail)

Output file (if invalid) contains header and identified invalid records

"""

# Configure logging to emit to STDOUT by default
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d  %(levelname)-10s%(funcName)-22s%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class ParseDelimitedFile:
    r"""
    A class that parses passed filename by delimiter to verify header record delimiter counts
    match each detail record

    :Example:
    >>> pdf = ParseDelimitedFile(',', r'C:\myfile.csv')

    Parameters:
        delimiter (str): The character used to separate fields in the file.
        filename (str): The path to the file to be checked.
    """

    ERROR_DELIMITER_FILE_SUFFIX = ".ERROR_DELIMITER"

    def __init__(self, delimiter, filename) -> None:
        self.delimiter = delimiter
        self.filename = filename
        self.badrecords = dict()
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Delimiter File Checker Initialized")
        self.logger.info(f"- Delimiter: {self.delimiter}")
        self.logger.info(f"-Filename : {self.filename}")
        self.logger.info("")

    def parse(self) -> None:
        """
        Reads passed delimiter and compares delimiter count of header record (first record) to each detail record
        """
        FILESUFFIX = (
            "_"
            + datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            + self.ERROR_DELIMITER_FILE_SUFFIX
        )

        dict_tally = {}
        header_delimiter_count = 0
        for record_count, record in self.read_delimited_record(self.filename):
            if record_count == 1:
                header_delimiter_count = record.count(self.delimiter)
                self.save_bad_record(record, record_count, header_delimiter_count)
                continue

            detail_delimiter_count = record.count(self.delimiter)
            if header_delimiter_count != detail_delimiter_count:
                self.save_bad_record(record, record_count, detail_delimiter_count)

            # capture delimiter length statistics
            try:
                dict_tally[detail_delimiter_count] += 1
            except KeyError:
                dict_tally[detail_delimiter_count] = 1

        if total_bad_records := len(self.badrecords) - 1:
            self.logger.info("Record Counts:")
            self.logger.info(f"Bad  : {total_bad_records}")
            self.logger.info(f"Total: {record_count}")
            self.logger.info("")
            self.logger.info("Delimiter Counts: (#delimiters: records)")
            self.logger.info("- " + str(header_delimiter_count) + ": 1 (header)")
            for k in dict_tally:
                self.logger.info(f"- {k}: {dict_tally[k]}")

            self.logger.info("")
            self.logger.info(f"Details: {self.filename + FILESUFFIX}")
            self.logger.info("")
            self.logger.info("Status: BAD")

            message = []
            message.append(f"filename : {self.filename}")
            message.append(f"delimiter: {self.delimiter}")
            message.append(f"fields   : {(f'{header_delimiter_count/10000:.4f}')[-4:]}")
            message.append("\n\nDelimiter Count Summary:\n")
            message.append("\n".join([f"{k}: {dict_tally[k]}" for k in dict_tally]))
            message.append("\n\nDelimiter Header and Bad Record Detail:\n")
            for key in sorted(self.badrecords.keys()):
                message.append(f"{key}: {self.badrecords[key]}\n")

            # write output file to include filename, delimiter, expected fields and all bad records record#, fieldcount, record (including header)
            with open(self.filename + FILESUFFIX, "w", encoding="utf-8") as badfile:
                badfile.write("".join(message))
            sys.exit(1)

        self.logger.info("Status: GOOD")
        sys.exit(0)

    def read_delimited_record(self, filename: str) -> Iterable[tuple[int, str]]:
        """
        Reads each record's count and data from passed filename using a generator pattern
        Args:
            filename: The path to the file to be read.

        Yields:
            record (generator object)
            record count (int)
            record data (str)
        """
        ctr = 0
        try:
            with open(
                filename, "r", encoding="utf-8"
            ) as csvfile:  # open filename with file handle
                for record in csv.reader(csvfile, delimiter=self.delimiter):
                    ctr += 1
                    if len(str(record).strip()) > 0:
                        yield ctr, self.delimiter.join(record)

        except UnicodeDecodeError as err:
            message = f"\nRecord: {ctr}\nError: {err}"
            self.logger.error(message)
            raise err

    def save_bad_record(
        self, record: str, record_count: int, delimiter_count: int
    ) -> None:
        self.badrecords[f"{record_count + delimiter_count / 10000:0>14.4f}"] = record


DEBUG = False
if __name__ == "__main__":
    parser = ap.ArgumentParser(
        description="Check file delimiter counts to verify detail vs. header",
        epilog=HELP_EPILOG,
        formatter_class=ap.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "delimiter", type=str, default=",", help="Input file CSV delimiter"
    )
    parser.add_argument("filename", type=str, help="Input filename")

    if DEBUG:
        args = parser.parse_args(
            args=[
                ",",
                r".\data\badfile.csv",
            ]
        )
    else:
        args = parser.parse_args()

    delimiter = args.delimiter
    filename = args.filename
    pdf = ParseDelimitedFile(delimiter, filename)
    pdf.parse()
