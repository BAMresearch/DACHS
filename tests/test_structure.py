# -*- coding: utf-8 -*-
# test_structure.py

from pathlib import Path

from mcsas3 import McHDF

import dachs.serialization
import dachs.structure


def test_integral() -> None:
    basepath = Path("tests", "testData")
    exp = dachs.structure.create(
        basepath / "AutoMOFs_Logbook_Testing.xlsx",
        [
            basepath / "AutoMOFs05_Solution0.xlsx",
            basepath / "AutoMOFs05_Solution1.xlsx",
        ],
        basepath / "AutoMOFs05_H005.xlsx",
    )

    dump = dachs.serialization.dumpKV("DACHS", exp)
    # from pprint import pprint
    # pprint(dump)
    McHDF.storeKVPairs(f"{exp.ID}_H005.h5", "", dump.items())
