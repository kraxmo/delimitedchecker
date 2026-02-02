#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@purpose: This script checks for embedded pipe characters within pipe-delimited file
          where header count != detail count and optionally writes bad records to output file
@author : Jim Kraxberger
@created: 2021-11-16
@updated: 2026-01-12
@command: (UNIX)    python delimitedfilechecker.py ',' 'filename' -w
          (Windows) python delimitedfilechecker.py "," "filename" -w
"""

import argparse
import csv
from datetime import datetime
import logging
import sys
from typing import Iterable

DEBUG = False
HELP_EPILOG = """

The purpose of this script is to check file delimiter count mismatches (header vs. detail)

Output file (if invalid) contains header and identified invalid records
"""

# Configure logging to emit to STDOUT by default
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s.%(msecs)03d | %(levelname)-10s | %(funcName)-22s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class ParseDelimitedFile:
    r"""
    A class that parses passed filename by delimiter to verify header record delimiter counts
    match each detail record

    :Example:
    >>> pdf = ParseDelimitedFile(',', r'C:\myfile.csv')

    :Parameters:
    >>> delimiter (str): The character used to separate fields in the file.
    >>> filename (str): The path to the file to be checked.
    >>> writeoutputfile (bool): Flag to indicate whether to write output file if bad records are found. (Default True)
    >>> ignore_over_count (bool): Flag to indicate whether to ignore records with over header delimiter count. (Default False)
    >>> expected_delimiter_count (int): The expected number of delimiters per record. (Default 0 = maximum).
    >>> batch_id (str): An optional batch process identifier. (Default '' empty string)
    """

    ERROR_DELIMITER_FILE_SUFFIX = ".ERROR_DELIMITER"
    BAD_RECORD_REPORTING_THRESHOLD = 100
    FILESUFFIX = (
        "_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ERROR_DELIMITER_FILE_SUFFIX
    )

    def __init__(
        self,
        delimiter: str,
        filename: str,
        write_output_file: bool = True,
        ignore_over_count: bool = False,
        expected_delimiter_count: int = 0,
        batch_id: str = "",
    ) -> None:
        self.delimiter = delimiter
        self.filename = filename
        self.write_output_file = write_output_file
        self.ignore_over_count = ignore_over_count
        self.expected_delimiter_count = (
            0 if expected_delimiter_count <= 0 else expected_delimiter_count
        )
        if batch_id:
            self.batch_id = f"({batch_id}) "
        else:
            self.batch_id = ""
        self.bad_records = {}

        self.logger = logging.getLogger(__name__)
        self.logger.info("%sDelimiter File Checker Initialized", self.batch_id)
        self.logger.info("%s- Delimiter: %s", self.batch_id, self.delimiter)
        self.logger.info("%s- Filename : %s", self.batch_id, self.filename)
        if expected_delimiter_count > 0:
            self.logger.info(
                "%s- Expected Delimiter Count: %s",
                self.batch_id,
                self.expected_delimiter_count,
            )
        self.logger.info(
            "%s- Write Output File if Bad Records Found: %s",
            self.batch_id,
            self.write_output_file,
        )
        self.logger.info(
            "%s- Ignore Over Count Records: %s", self.batch_id, self.ignore_over_count
        )

    def parse_records(self) -> int:
        """
        Reads passed delimiter and compares delimiter count of header record (first record) to each detail record

        Returns:
            int: header delimiter count if all records match header delimiter count, 0 otherwise if bad records found
        """
        delimiters_found = {}
        header_delimiter_count = 0
        record_count = 0
        nested_delimiter_count = 0
        max_record_length = 0
        record_over_count = 0
        record_under_count = 0
        record_equal_count = 0
        actual_not_expected_delimiter_count = 0
        for (
            record_count,
            record_length,
            record_fields,
        ) in self.read_delimited_record(self.filename):
            if record_length > max_record_length:
                max_record_length = record_length

            # record_fields is the list of parsed fields
            # join produces record string for storage/logging and compute field_count
            record = self.delimiter.join(record_fields)
            field_count = len(record_fields)

            # count records that contain nested delimiters inside a field
            if any(self.delimiter in f for f in record_fields):
                nested_delimiter_count += 1

            # Use the number of parsed fields (not raw delimiter characters)
            # to correctly handle nested delimiters inside quoted fields.
            if record_count == 1:
                header_delimiter_count = field_count - 1
                self.save_bad_records(record, record_count, header_delimiter_count)
                continue

            if record_count % 100000 == 0:
                self.logger.info(f"{self.batch_id}Processed {record_count} records...")

            detail_delimiter_count = field_count - 1
            if detail_delimiter_count > header_delimiter_count:
                record_over_count += 1
            elif detail_delimiter_count == header_delimiter_count:
                record_equal_count += 1
            else:
                record_under_count += 1

            if (
                self.expected_delimiter_count > 0
                and detail_delimiter_count != self.expected_delimiter_count
            ):
                actual_not_expected_delimiter_count += 1

            if (header_delimiter_count != detail_delimiter_count) or (
                self.expected_delimiter_count > 0
                and detail_delimiter_count != self.expected_delimiter_count
            ):
                self.save_bad_records(record, record_count, detail_delimiter_count)

            # capture delimiter length statistics
            try:
                delimiters_found[detail_delimiter_count] += 1
            except KeyError:
                delimiters_found[detail_delimiter_count] = 1

        bad_record_count = len(self.bad_records) - 1  # exclude header record
        self.logger.info("%s", self.batch_id)
        if len(self.bad_records) - 1 == 0:
            self.logger.info("%sDelimited Record Counts:", self.batch_id)
            self.logger.info(
                "%s- Delimiter count: %d", self.batch_id, header_delimiter_count
            )
            self.logger.info("%s- Total records  : %d", self.batch_id, record_count)
            self.logger.info("")
            self.logger.info("%sFile is GOOD", self.batch_id)
            return header_delimiter_count

        if self.ignore_over_count and record_over_count > 0 and record_under_count == 0:
            self.logger.info(
                "%sFile is FAIR (ignoring %d overcount records)",
                self.batch_id,
                bad_record_count,
            )
            return header_delimiter_count

        self.logger.info("%sFile is BAD", self.batch_id)
        if actual_not_expected_delimiter_count:
            self.logger.info(
                "%s- Possible reasons: correct filename/wrong data or wrong file",
                self.batch_id,
            )
        self.logger.info(f"{self.batch_id}")
        self.logger.info("%sDelimited Record Counts:", self.batch_id)
        self.logger.info("%s- Header : 1", self.batch_id)
        self.logger.info("%s- Bad    :", self.batch_id)
        self.logger.info("%s  + Under: %d", self.batch_id, record_under_count)
        self.logger.info("%s  + Equal: %d", self.batch_id, record_equal_count)
        self.logger.info("%s  + Over : %d", self.batch_id, record_over_count)
        self.logger.info("%s- Nested : %d", self.batch_id, nested_delimiter_count)
        self.logger.info("%s- Total  : %d", self.batch_id, record_count)
        self.logger.info("%s", self.batch_id)
        self.logger.info("%sDelimiter Counts: (#delimiters: records)", self.batch_id)
        self.logger.info("%s- %d: 1 (header)", self.batch_id, header_delimiter_count)
        for k in delimiters_found:
            self.logger.info("%s- %d: %d", self.batch_id, k, delimiters_found[k])

        self.logger.info("")
        if (self.expected_delimiter_count > 0) and (
            self.expected_delimiter_count != header_delimiter_count
        ):
            self.logger.info(
                "%s*PROBLEM Mismatched Delimiters: Expected %d but found %d records with different delimiter counts",
                self.batch_id,
                self.expected_delimiter_count,
                actual_not_expected_delimiter_count,
            )

        if self.write_output_file:
            self.logger.info("%s", self.batch_id)
            self.logger.info(
                "%sDetails: %s", self.batch_id, self.filename + self.FILESUFFIX
            )

        message = []
        message.append("Bad Delimited File Check Report:\n")
        message.append(f"filename       : {self.filename}")
        message.append(f"\ndelimiter value: {self.delimiter}")
        message.append(
            f"\ndelimiter count: {(f'{header_delimiter_count/10000:.4f}')[-4:]}"
        )
        if self.expected_delimiter_count:
            message.append(
                f"\nexpected  count: {(f'{self.expected_delimiter_count/10000:.4f}')[-4:]}"
            )
        message.append("\n\nDelimiter Record Count Summary:\n")
        message.append("dcnt records\n")
        message.append("---- --------\n")
        message.append(
            "\n".join(
                [f"{k:0>4d}:{delimiters_found[k]:0>8d}" for k in delimiters_found]
            )
        )

        if (self.expected_delimiter_count > 0) and (
            self.expected_delimiter_count != header_delimiter_count
        ):
            message.append(
                f"\n\n*PROBLEM Mismatched Delimiters: Expected {self.expected_delimiter_count} but found {actual_not_expected_delimiter_count} records with different delimiter counts"
            )

        message.append(
            f"\n\n{'Top ' + str(self.BAD_RECORD_REPORTING_THRESHOLD) if record_count >= self.BAD_RECORD_REPORTING_THRESHOLD else 'All'} Bad Record Delimiter Detail:\n"
        )
        message.append(f" record#  dcnt data\n")
        message.append(f"--------- ---- {'-'*max_record_length}\n")
        for counter, key in enumerate(sorted(self.bad_records.keys()), start=1):
            if counter <= self.BAD_RECORD_REPORTING_THRESHOLD:
                if counter == 1:
                    message.append(f"{key}:{self.bad_records[key]} (header)\n")
                else:
                    message.append(f"{key}:{self.bad_records[key]}\n")
            elif counter == self.BAD_RECORD_REPORTING_THRESHOLD:
                self.logger.info(
                    "%sBad record count exceeded %d record threshold",
                    self.batch_id,
                    self.BAD_RECORD_REPORTING_THRESHOLD,
                )

        if self.write_output_file:
            # write output file to include filename, delimiter, expected fields and all bad records record#, fieldcount, record (including header)
            with open(
                self.filename + self.FILESUFFIX, "w", encoding="utf-8"
            ) as badfile:
                badfile.write("".join(message))

        return 0

    def read_delimited_record(self, filename: str) -> Iterable[tuple[int, int, list]]:
        """
        Reads each record into delimited fields
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
                    self.logger.debug(f"{self.batch_id}Record {ctr}: {record}")
                    total_field_length = sum(len(rec) for rec in record)
                    delimiter_count = len(record) - 1
                    record_length = total_field_length + delimiter_count
                    if record_length > 0:
                        # return the parsed record fields (list) so callers
                        # can inspect individual fields (e.g. to detect
                        # nested delimiters inside quoted fields)
                        yield ctr, record_length, record

        except FileNotFoundError:
            self.logger.error("%sFile not found", self.batch_id)
            sys.exit(1)

        except UnicodeDecodeError as err:
            message = f"\n{self.batch_id}Record: {ctr}\nError: {err}"
            self.logger.error(message, err)
            sys.exit(1)

    def save_bad_records(
        self, record: str, record_count: int, delimiter_count: int
    ) -> None:
        """Saves bad record with unique key counts"""
        self.bad_records[f"{record_count + delimiter_count / 10000:0>14.4f}"] = record


def get_args() -> argparse.Namespace:
    """
    Setup and run delimited directory checker
    """
    parser = argparse.ArgumentParser(
        description="Check file delimiter counts to verify detail vs. header",
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "delimiter", type=str, default=",", help="Input file CSV delimiter"
    )
    parser.add_argument("filename", type=str, help="Input filename")
    parser.add_argument(
        "-w",
        "--writeoutputfile",
        action="store_true",
        help="Write output file if bad records found",
    )
    parser.add_argument(
        "-i",
        "--ignoreovercount",
        action="store_true",
        help="Ignore records with over header delimiter count (default: No)",
    )
    parser.add_argument(
        "-d",
        "--delimiter_count",
        type=int,
        default=0,
        help="Expected delimiter count",
    )
    parser.add_argument(
        "-b", "--batchid", type=str, default="", help="Batch process identifier"
    )

    if DEBUG:
        args = parser.parse_args(
            args=[
                ",",
                r".\data\badunder.csv",
                "-w",
                "-b",
                "TESTBATCH01",
            ]
            # args=[
            #     ",",
            #     r".\data\goodfile.csv",
            #     "-w",
            #     "--delimiter_count",
            #     "3",
            # ]
        )
    else:
        args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()
    delimiter = args.delimiter
    filename = args.filename
    delimiter_count = args.delimiter_count
    ignore_over_count = True if args.ignoreovercount else False
    write_output_file = True if args.writeoutputfile else False
    batch_id = args.batchid

    pdf = ParseDelimitedFile(
        delimiter,
        filename,
        write_output_file,
        ignore_over_count,
        delimiter_count,
        batch_id,
    )
    if pdf.parse_records():
        sys.exit(0)
    else:
        sys.exit(1)
