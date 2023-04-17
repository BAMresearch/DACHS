#!/usr/bin/env python
# coding: utf-8

import argparse
import logging
from pathlib import Path

from mcsas3 import McHDF

import dachs.serialization
import dachs.structure


def outfileFromInput(infn, suffix="h5"):
    return Path(infn).resolve().with_suffix(f".{suffix}")


def configureParser() -> argparse.ArgumentParser:
    def validate_file(arg):
        if (file := Path(arg).absolute()).is_file():
            return file
        else:
            raise FileNotFoundError(arg)

    # process input arguments
    parser = argparse.ArgumentParser(
        prog=__package__,
        description="""
            Creates an archival HDF5 structure containing synthesis details from a RoWaN AutoMOF synthesis.

            Released under a GPLv3+ license.
            """,
    )
    defaultPath = Path(__file__).resolve().parent.parent.parent / "tests" / "testData"
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
        help="File containing the synthesis log of Solution 0",
        required=True,
    )
    parser.add_argument(
        "-s1",
        "--s1file",
        type=validate_file,
        default=defaultPath / "AutoMOFs05_Solution1.csv",
        help="File containing the synthesis log of Solution 1",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--synlog",
        type=validate_file,
        default=defaultPath / "AutoMOFs05_H005.csv",
        help="File containing the synthesis log of the MOF itself.",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--outfile",
        help=(
            "Output file containing structured HDF5 data. "
            "If omitted, it is written to the same directory "
            "and with the same basename as *synlog* above, but with .h5 suffix."
        ),
    )
    return parser


if __name__ == "__main__":
    args = configureParser().parse_args()
    if not args.outfile:
        args.outfile = outfileFromInput(args.synlog)

    exp = dachs.structure.create(args.logbook, (args.s0file, args.s1file), args.synlog)
    dump = dachs.serialization.dumpKV(exp)
    # from pprint import pprint
    # pprint(dump)
    logging.info(f"Writing structure to '{args.outfile}'.")
    McHDF.storeKVPairs(args.outfile, "", dump.items())
    print("Types found in McHDF serialized data:", {type(value) for path, value in dump.items()})
    paths, graph = dachs.serialization.buildGraph2(exp, dbg=True)
    dachs.serialization.graphKV(paths)
    graph.render(graph.name, cleanup=True)
