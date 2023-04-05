#!/usr/bin/env python
# coding: utf-8

import argparse
from pathlib import Path

from mcsas3 import McHDF

import dachs.structure


def configureParser() -> argparse.ArgumentParser:
    def validate_file(arg):
        if (file := Path(arg).absolute()).is_file():
            return file
        else:
            raise FileNotFoundError(arg)

    # process input arguments
    parser = argparse.ArgumentParser(
        description="""
            Creates an archival HDF5 structure containing synthesis details from a RoWaN AutoMOF synthesis.

            Released under a GPLv3+ license.
            """
    )
    defaultPath = Path(__file__).absolute().parent / "tests" / "testData"
    # TODO: add info about output files to be created ...
    parser.add_argument(
        "-l",
        "--logbook",
        type=validate_file,
        default=defaultPath / "AutoMOFs_Logbook_Working.csv",
        help="Path to the filename containing the main AutoMOF logbook",
        # nargs="+",
        required=True,
    )
    parser.add_argument(  # could perhaps be done with a multi-file input for multiple solutions...
        "-s0",
        "--s0file",
        type=validate_file,
        default=defaultPath / "AutoMOFs05_Solution0.csv",
        help="File containing the syntheiss log of Solution 0",
        required=True,
    )
    parser.add_argument(
        "-s1",
        "--s1file",
        type=validate_file,
        default=defaultPath / "AutoMOFs05_Solution1.csv",
        help="File containing the syntheiss log of Solution 1",
        required=True,
    )
    parser.add_argument(
        "-f",
        "--filename",
        type=validate_file,
        default=defaultPath / "AutoMOFs05_H005.csv",
        help="File containing the synthesis log of the MOF itself.",
        required=True,
    )

    return parser


if __name__ == "__main__":
    parser = configureParser()

    try:
        args = parser.parse_args()
    except SystemExit:
        raise
    adict = vars(args)

    exp = dachs.structure.create(
        adict["logbook"],
        [
            adict["s0file"],
            adict["s1file"],
        ],
        adict["filename"],
    )

    # Export everything finally
    from dachs.serialization import storagePaths

    dump = storagePaths("DACHS", exp)
    # from pprint import pprint
    # pprint(dump)
    ofname = adict["filename"].absolute().with_suffix(".h5")
    print(f"{ofname=}")

    for key, value in dump.items():
        # extracting path from keys could be added to McHDF.storeKVPairs()
        try:
            McHDF.storeKV(filename=ofname, path=key, value=value)
        except Exception:
            print(f"Error for path {key} and value '{value}' of type {type(value)}.")
            raise
