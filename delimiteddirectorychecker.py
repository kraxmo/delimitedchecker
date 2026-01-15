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
import sys
from pathlib import Path
from typing import Generator, Iterable, Union


class ParseDelimitedDirectory:
    def __init__(
        self, delimiter: str, directory: str, filesuffix: str, verbosemode: bool
    ) -> None:
        self.delimiter = delimiter
        # self.directory = os.path.normpath(directory)
        self.directory = Path(directory).resolve()
        if not (self.directory.exists() and self.directory.is_dir()):
            print(f"The directory '{directory}' does not exist or is not a directory.")
            return sys.exit(1)

        self.filesuffix = filesuffix
        if self.filesuffix:
            self.filesuffix = "." + filesuffix

        self.verbosemode = verbosemode

    def iter_files_by_extension(
        self,
        root: Union[str, Path],
        extensions: Union[str, Iterable[str]],
    ) -> Generator[Path, None, None]:
        """
        Recursively walk `root` and yield files whose extension matches `extensions`.
        Works on Windows, macOS, and Linux.

        Args:
            root: Starting directory (supports Windows drive letters and UNC paths).
            extensions: A single extension (e.g., ".csv" or "csv") or an iterable of them.
                        Matching is case-insensitive. Leading dots are optional.
            follow_symlinks: If True, include symlinked files/dirs. Default False.

        Yields:
            Path objects for each matching file.
        """
        root_path = Path(root)

        # Normalize extensions: ensure leading dot and lowercase.
        if isinstance(extensions, (str, Path)):
            norm_exts = {"." + str(extensions).lower().lstrip(".")}
        else:
            norm_exts = {("." + str(ext).lower().lstrip(".")) for ext in extensions}

        # Iterate recursively. pathlib handles Windows separators and UNC paths.
        for path in root_path.rglob("*"):
            # Skip directories
            if path.is_dir():
                continue

            if path.suffix.lower() in norm_exts:
                yield path

    def parse_directory(self):
        """
        Reads passed directory's files and calls delimitedfilechecker with delimiter and file
        """
        if self.verbosemode:
            print("\n" + "=" * 50)
            print(
                f"delimitedfilechecker\n- delimiter  : {self.delimiter}\n- directory  : {self.directory}\n- filesuffix     : {self.filesuffix}\n- verbosemode: {self.verbosemode}"
            )
            print("=" * 50)

        if not os.path.exists(self.directory):
            print(f"Error: directory '{self.directory} does not exist.")
            return

        if not os.path.isdir(self.directory):
            print(f"Error: path '{self.directory} is not a directory.")

        error_count = 0
        print(f"DIRECTORY: {self.directory}")
        # for file in self.read_directory_files():
        for filename in self.iter_files_by_extension(
            self.directory, self.filesuffix.lstrip(".")
        ):
            try:
                d = dfc.ParseDelimitedFile(self.delimiter, str(filename), True)
                if not d.parse_records():
                    error_count += 1
            except Exception as e:
                print(f"Exception: {e}")
                error_count += 1
            finally:
                if self.verbosemode:
                    print("-" * 50)

        if error_count:
            message = f"Directory {self.directory} has {error_count} badly delimited file{'s' if error_count > 1 else ''}"
            message += "\n- See directory files with filesuffix _ERROR_DELIMITER_YYYY_MM_DD_HH_MM_DD for details"
            print(message)
            sys.exit(1)


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
    parser.add_argument(
        "delimiter", type=str, default=",", help="Input file CSV delimiter"
    )
    parser.add_argument("directory", type=str, help="Input directory")
    parser.add_argument(
        "-f",
        "--filesuffix",
        type=str,
        default="csv",
        help="File suffix (default: csv), no suffix = ''",
    )
    parser.add_argument(
        "-v",
        "--verbosemode",
        action="store_true",
        help="Verbose mode: True = print process messages, False(default) = omit process messages",
    )
    return parser.parse_args()


DEBUG = True
HELP_EPILOG = """

The purpose of this script is to check all files in specified directory for delimiter counts mismatches (header vs. detail)

"""

if __name__ == "__main__":
    if DEBUG:
        args = ap.Namespace(
            delimiter=",", directory=r".\data", filesuffix="csv", verbosemode=True
        )
    else:
        args = get_args()

    pdd = ParseDelimitedDirectory(
        args.delimiter, args.directory, args.filesuffix, args.verbosemode
    )
    pdd.parse_directory()
