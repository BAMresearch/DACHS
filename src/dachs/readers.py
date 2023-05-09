#!/usr/bin/env python
# coding: utf-8

"""
Contains readers for loading and interpreting the excel files of Glen and the log files of RoWaN
"""

__author__ = "Brian R. Pauw"
__contact__ = "brian@stack.nl"
__license__ = "GPLv3+"
__date__ = "2022/12/12"
__status__ = "beta"

# import numpy as np


from pathlib import Path
from typing import List, Optional, Union

import chempy
import pandas as pd
import pint
import yaml

from dachs import ureg
from dachs.equipment import Equipment
from dachs.helpers import whitespaceCleanup
from dachs.metaclasses import ExperimentalSetupClass
from dachs.reagent import Chemical, Reagent
from dachs.synthesis import RawLogMessage, synthesisStep


def readExperimentalSetup(filename: Path, SetupName: str = "AMSET_6") -> ExperimentalSetupClass:
    #     filename = Path("tests", "testData", "AutoMOFs_Logbook_Testing.xlsx")
    # SetupName='AMSET_6'

    assert filename.exists()

    # read equipment list:
    eq = pd.read_excel(filename, sheet_name="Equipment", index_col=None, header=0)
    eq = eq.dropna(how="all")
    eqDict = {}
    for rowi, equip in eq.iterrows():
        try:
            eqItem = Equipment(
                ID=str(equip["Equipment ID"]),
                Name=str(equip["Equipment Name"]),
                Manufacturer=str(equip["Manufacturer"]),
                ModelName=str(equip["Model Name"]),
                ModelNumber=str(equip["Model Number"]),
                UnitPrice=ureg.Quantity(str(equip["Unit Price"]) + " " + str(equip["Price Unit"])),
                UnitSize=ureg.Quantity(str(equip["Unit Size"]) + " " + str(equip["Unit"])),
                Description=whitespaceCleanup(equip["Description"]),
                PVs=[],
                # todo remove these later once PVs are configured. 
                CalibrationFactor=float(equip['Calibration Factor']),   
                CalibrationOffset=ureg.Quantity(str(equip['Calibration Offset'])),   
            )
            eqDict.update({str(equip["Equipment ID"]): eqItem})
        except Exception as e:
            print(f'Failure reading {equip["Equipment ID"]=}\n {str(e)}')

    # read setup configuration:
    df = pd.read_excel(filename, sheet_name="Setup", index_col=None, header=0)
    df = df.dropna(how="all")  # "If all values are NA, drop that row or column." - right?
    dfRow = df.loc[df.SetupID == SetupName].copy()
    assert len(dfRow == 1), f"More or less than one entry found for {SetupName=} in {filename=}"
    # get all equipment for the setup
    itemList = [dfRow[i].item() for i in dfRow.keys() if "ID_" in i]
    eqList = [eqDict[item] for item in itemList if item in eqDict.keys()]
    expSetup = ExperimentalSetupClass(
        ID=dfRow.SetupID.item(),
        Name=dfRow.Name.item(),
        Description=whitespaceCleanup(dfRow.Description.item()),
        EquipmentList=eqList,
    )
    return expSetup


def readRawMessageLog(filename: Path) -> List:
    # filename = Path("tests", "testData", "AutoMOFs05_H005.xlsx")
    assert filename.exists()
    df = pd.read_excel(filename, sheet_name="Sheet1", index_col=None, header=0, parse_dates=["Time"])
    df = df.dropna(how="all")
    df.sort_values(by='Time', ignore_index=True, inplace=True)
    msgList = []
    for idx, row in df.iterrows():
        condition = 0
        Val, U, Q = None, None, None
        if row["Value"].strip() != "-":
            Val = yaml.safe_load(row["Value"]) if isinstance(row["Value"], str) else row["Value"]
            condition += 1
        if row["Unit"].strip() != "-":
            U = row["Unit"].strip()
            U = "percent" if U == "%" else U
            U = "degC" if U == "C" else U
            U = "minute" if U == "mins" else U
            # U=ureg.parse_units(U)
            condition += 1
        if condition == 2:  # both value and unit are present
            try:
                Q = ureg.Quantity(Val, str(U))
            except pint.PintError:  # conversion fail
                Q = None

        msgList += [
            RawLogMessage(
                Index=idx,
                TimeStamp=row["Time"],
                MessageLevel=row["Info"],
                ExperimentID=row["ExperimentID"],
                SampleID=row["SampleNumber"],
                Message=row["Readout"],
                Unit=U,
                Value=Val,
                Quantity=Q,
            )
        ]
    return msgList


def ReadStartingCompounds(filename) -> List:
    assert filename.exists()
    df = pd.read_excel(
        filename,
        sheet_name="Chemicals",
        index_col=None,
        header=0,
        parse_dates=["Open Date"],
    )
    df = df.dropna(how="all")
    # Turn the specified chemicals into a list of starting compounds
    cList = []
    for idx, row in df.iterrows():
        # print(f"{idx=}, {row=}")
        s = chempy.Substance.from_formula(row["Formula"])
        cList += [
            Reagent(
                ID=str(row["Reagent ID"]),
                Chemical=Chemical(
                    ID=row["Reagent ID"],
                    Name=row["Name"],
                    ChemicalFormula=row["Formula"],
                    Substance=s,
                    MolarMass=ureg.Quantity(str(s.molar_mass())).to(
                        "g/mol"
                    ),  # assert_unit(row["Molar Mass"], "g/mol"),
                    Density=ureg.Quantity(str(row["Density"]) + " g/cm^3"),
                ),
                CASNumber=row["CAS-Number"],
                Brand=row["Brand"],
                UNNumber=row["UN-Number"],
                MinimumPurity=assert_unit(row["Purity"], "percent"),
                OpenDate=row["Open Date"],
                StorageConditions=row["Storage Conditions"],
                UnitPrice=assert_unit(row["Unit Price"], "euro"),
                UnitSize=assert_unit(row["Unit Size"], row["Unit"]),
            )
        ]
    return cList


def assert_unit(value, default_unit: str) -> str:
    """
    adds a default unit string for interpretation by pint
    if the value is not in string format yet
    (and therefore does not yet have a unit)
    """
    # print(f"{value=}, {default_unit=}")
    if not isinstance(value, str):
        return str(value) + " " + str(default_unit)
    else:
        return value


def find_trigger_in_log(logEntry: synthesisStep, triggerList=["Weight"]) -> bool:
    """
    Interprets a synthesis step. If a word in the triggerList is found,
    it returns True, otherwise False
    """
    triggerFound = False
    for trigger in triggerList:
        if trigger in logEntry.RawMessage:
            triggerFound = True
    return triggerFound


def find_reagent_in_rawmessage(searchString: str, ReagentList: List[Reagent]) -> Optional[Reagent]:
    """
    Returns (the first match of) a given Reagent if its ID is found in an input string,
    otherwise returns None
    """
    for reag in ReagentList:
        if reag.ID in searchString:
            return reag
    return None


def find_in_log(
    log: List[RawLogMessage],
    searchString: Union[str, list],
    excludeString: Union[str, list]='Dummy exclude string which will not be found',
    Highlander: bool = True,  # there can be only one if Highlander is True
    Which: str = "first",  # if highlander, specify if first or last
) -> Optional[Union[RawLogMessage, list[RawLogMessage]]]:
    """
    Returns (the first match of) a given Reagent if its ID is found in an input string,
    otherwise returns None
    """
    answers = []
    if isinstance(searchString, str):
        searchString = [searchString]
    if isinstance(excludeString, str):
        excludeString = [excludeString]
    for RLM in log:
        if all(i.lower() in RLM.Message.lower() for i in searchString) and not any(j.lower() in RLM.Message.lower() for j in excludeString):
            if Highlander:
                answers = RLM
                if Which.lower() == "first":
                    return RLM
            else:
                answers += [RLM]
    return answers
