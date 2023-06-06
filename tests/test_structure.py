# -*- coding: utf-8 -*-
# test_structure.py

from os import environ
from pathlib import Path

from dachs.main import main

# import sys
# defaultPath = Path(__file__).resolve().parent / "src"
# sys.path.append(defaultPath)

basepath = Path(__file__).parent / "testData"


def test_integral() -> None:
    environ["DACHS_LOGBOOK"] = str(basepath / "AutoMOFs_Logbook_Testing.xlsx")
    environ["DACHS_AMSET"] = "AMSET_6"
    for s0, s1, syn in (
        ("AutoMOFs05_Solution0.xlsx", "AutoMOFs05_Solution1.xlsx", "AutoMOFs05_H005.xlsx"),
        ("log_AutoMOFs_6_Solution0.xlsx", "log_AutoMOFs_6_Solution1.xlsx", "log_AutoMOFs_6_L019.xlsx"),
    ):
        environ["DACHS_SOL0"] = str(basepath / s0)
        environ["DACHS_SOL1"] = str(basepath / s1)
        environ["DACHS_SYNLOG"] = str(basepath / syn)
        main()


if __name__ == "__main__":
    test_integral()
