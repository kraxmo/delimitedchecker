#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@purpose: This script checks for embedded pipe characters within pipe-delimited file
          where header count != detail count and optionally writes bad records to output file
@author : Jim Kraxberger
@created: 2021-11-16
@updated: 2026-01-12
@command: (UNIX)    python delimitedfilechecker.py ',' 'filename', True
          (Windows) python delimitedfilechecker.py "," "filename", True
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
Output file threshold can be set to limit number of bad records reported
"""

BAD_RECORD_THRESHOLD = 100

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
        writeoutputfile (bool): Flag to indicate whether to write output file if bad records are found. Default is True.
        badrecordthreshold (int): Threshold for bad records before stopping logging bad records.
    """

    ERROR_DELIMITER_FILE_SUFFIX = ".ERROR_DELIMITER"
    BAD_RECORD_THRESHOLD = 100

    def __init__(
        self,
        delimiter: str,
        filename: str,
        write_output_file: bool = True,
        bad_record_threshold: int = BAD_RECORD_THRESHOLD,
    ) -> None:
        self.delimiter = delimiter
        self.filename = filename
        self.write_output_file = write_output_file
        self.bad_record_threshold = bad_record_threshold

        self.badrecords = dict()
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Delimiter File Checker Initialized")
        self.logger.info(f"- Delimiter: {self.delimiter}")
        self.logger.info(f"- Filename : {self.filename}")
        self.logger.info("")

    def parse_records(self) -> int:
        """
        Reads passed delimiter and compares delimiter count of header record (first record) to each detail record

        Returns:
            int: header delimiter count if all records match header delimiter count, 0 otherwise if bad records found
        """
        FILESUFFIX = (
            "_"
            + datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            + self.ERROR_DELIMITER_FILE_SUFFIX
        )

        dict_tally = {}
        header_delimiter_count = 0
        record_count = 0
        nested_count = 0
        max_record_length = 0
        for record_count, record_length, record_fields in self.read_delimited_record(
            self.filename
        ):
            if record_length > max_record_length:
                max_record_length = record_length

            # record_fields is the list of parsed fields
            # join produces record string for storage/logging and compute field_count
            record = self.delimiter.join(record_fields)
            field_count = len(record_fields)

            # count records that contain nested delimiters inside a field
            if any(self.delimiter in f for f in record_fields):
                nested_count += 1

            # Use the number of parsed fields (not raw delimiter characters)
            # to correctly handle nested delimiters inside quoted fields.
            if record_count == 1:
                header_delimiter_count = field_count - 1
                self.save_bad_record(record, record_count, header_delimiter_count)
                continue

            if record_count % 100000 == 0:
                self.logger.info(f"Processed {record_count} records...")

            detail_delimiter_count = field_count - 1
            if header_delimiter_count != detail_delimiter_count:
                self.save_bad_record(record, record_count, detail_delimiter_count)

            # capture delimiter length statistics
            try:
                dict_tally[detail_delimiter_count] += 1
            except KeyError:
                dict_tally[detail_delimiter_count] = 1

        if total_bad_records := len(self.badrecords) - 1:
            self.logger.info("Delimited Record Counts:")
            self.logger.info(f"- Bad   : {total_bad_records}")
            self.logger.info(f"- Nested: {nested_count}")
            self.logger.info(f"- Total : {record_count}")
            self.logger.info("")
            self.logger.info("Delimiter Counts: (#delimiters: records)")
            self.logger.info("- " + str(header_delimiter_count) + ": 1 (header)")
            for k in dict_tally:
                self.logger.info(f"- {k}: {dict_tally[k]}")

            self.logger.info("")
            self.logger.info("File is BAD")
            if self.write_output_file:
                self.logger.info(f"Details: {self.filename + FILESUFFIX}")

            message = []
            message.append("Bad Delimited File Check Report:\n")
            message.append(f"filename : {self.filename}")
            message.append(f"\ndelimiter: {self.delimiter}")
            message.append(
                f"\nfields   : {(f'{header_delimiter_count/10000:.4f}')[-4:]}"
            )
            message.append("\n\nDelimiter Record Count Summary:\n")
            message.append("dcnt records\n")
            message.append("---- --------\n")
            message.append(
                "\n".join([f"{k:0>4d}:{dict_tally[k]:0>8d}" for k in dict_tally])
            )
            message.append(
                f"\n\n{'Top ' + str(self.bad_record_threshold) if record_count >= self.bad_record_threshold else 'All'} Bad Record Delimiter Detail: (* identifies header record)\n"
            )
            message.append(f" record#  dcnt data\n")
            message.append(f"--------- ---- {'-'*max_record_length}\n")
            for counter, key in enumerate(sorted(self.badrecords.keys()), start=1):
                if counter <= self.bad_record_threshold:
                    if counter == 1:
                        message.append(f"{key}:*{self.badrecords[key]}\n")
                    else:
                        message.append(f"{key}: {self.badrecords[key]}\n")
                elif counter == self.bad_record_threshold:
                    self.logger.info(
                        f"Bad record count exceeded {self.bad_record_threshold} record threshold",
                    )

            if self.write_output_file:
                # write output file to include filename, delimiter, expected fields and all bad records record#, fieldcount, record (including header)
                with open(self.filename + FILESUFFIX, "w", encoding="utf-8") as badfile:
                    badfile.write("".join(message))

            return 0

        self.logger.info("File is GOOD")
        return header_delimiter_count

    def read_delimited_record(self, filename: str) -> Iterable[tuple[int, int, list]]:
        """
        Reads each record's count and data from passed filename using a generator pattern
        Args:
            filename: The path to the file to be read.

        Yields:
            tuple: (record_count (int), record_length (int), record_fields (list[str]))
        """
        ctr = 0
        try:
            with open(
                filename, "r", encoding="utf-8"
            ) as csvfile:  # open filename with file handle
                for record in csv.reader(csvfile, delimiter=self.delimiter):
                    ctr += 1
                    total_field_length = sum(len(rec) for rec in record)
                    delimiter_count = len(record) - 1
                    record_length = total_field_length + delimiter_count
                    if record_length > 0:
                        # return the parsed record fields (list) so callers
                        # can inspect individual fields (e.g. to detect
                        # nested delimiters inside quoted fields)
                        yield ctr, record_length, record

        except FileNotFoundError:
            self.logger.error("File not found error")
            raise SystemExit(1)

        except UnicodeDecodeError as err:
            message = f"\nRecord: {ctr}\nError: {err}"
            self.logger.error(message, err)
            raise sys.exit(1)

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
    parser.add_argument(
        "-w",
        "--writeoutputfile",
        action="store_true",
        help="Do not write output file if bad records found",
    )
    parser.add_argument(
        "-b",
        "--badrecordthreshold",
        type=int,
        nargs="?",
        default=BAD_RECORD_THRESHOLD,
        help=f"Bad record threshold before stopping logging bad records (default: {BAD_RECORD_THRESHOLD})",
    )

    if DEBUG:
        args = parser.parse_args(
            args=[
                ",",
                r".\data\badfile.csv",
                "-w",
                "-b",
                "3",
            ]
        )
    else:
        args = parser.parse_args()

    delimiter = args.delimiter
    filename = args.filename
    write_output_file = True if args.writeoutputfile else False
    bad_record_threshold = args.badrecordthreshold
    pdf = ParseDelimitedFile(
        delimiter, filename, write_output_file, bad_record_threshold
    )
    if pdf.parse_records():
        sys.exit(0)
    else:
        sys.exit(1)
