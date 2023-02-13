#!/usr/bin/env python
# coding: utf-8

"""
Overview:
========
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

import pandas as pd
import yaml
from dachs.equipment import equipment
from dachs.metaclasses import experimentalSetup
from dachs.reagent import chemical, reagent
from dachs.synthesis import RawLogMessage, synthesisStep
from dachs.__init__ import ureg

def readExperimentalSetup(filename:Path, SetupName:str='AMSET_6')-> experimentalSetup:
    #     filename = Path("tests", "testData", "AutoMOFs_Logbook_Testing.xlsx")
    # SetupName='AMSET_6'

    assert filename.exists()

    # read equipment list:
    eq = pd.read_excel(
        filename, sheet_name="Equipment", index_col=None, header=0
    )
    eq = eq.dropna(how="all") 
    eqDict={}
    for rowi,equip in eq.iterrows():
        try:
            eqItem=equipment(
                ID=str(equip['Equipment ID']),
                Name=str(equip['Equipment Name']),
                Manufacturer=str(equip['Manufacturer']),
                ModelName=str(equip['Model Name']),
                ModelNumber=str(equip['Model Number']),
                UnitPrice=ureg.Quantity(str(equip['Unit Price']) + " " + str(equip['Price Unit'])),
                UnitSize=ureg.Quantity(str(equip['Unit Size']) + " " + str(equip['Unit'])),
                Description=str(equip['Description']),
                PVs=[]
            )
            eqDict.update({str(equip['Equipment ID']): eqItem})
        except Exception as e:
            print(f'Failure reading {equip["Equipment ID"]=}\n {str(e)}')

    # read setup configuration:
    df = pd.read_excel(
        filename, sheet_name="Setup", index_col=None, header=0
    )
    df = df.dropna(how="all")
    dfRow = df.loc[df.SetupID==SetupName].copy()
    assert len(dfRow==1), f'More or less than one entry found for {SetupName=} in {filename=}'
    # get all equipment for the setup
    itemList = [dfRow[i].item() for i in dfRow.keys() if 'ID_' in i]
    eqList=[eqDict[item] for item in itemList if item in eqDict.keys()]
    expSetup = experimentalSetup(
        ID=dfRow['SetupID'],
        Name=dfRow['Name'],
        Description=dfRow['Description'],
        EquipmentList=eqList
    )
    return expSetup

def readRawMessageLog(filename: Path) -> List:
    # filename = Path("tests", "testData", "AutoMOFs05_H005.xlsx")
    assert filename.exists()
    df = pd.read_excel(
        filename, sheet_name="Sheet1", index_col=None, header=0, parse_dates=["Time"]
    )
    df = df.dropna(how="all")

    msgList = []
    for idx, row in df.iterrows():
        condition = 0
        Val, U, Q = None, None, None
        if row["Value"].strip() != "-":
            Val = (
                yaml.safe_load(row["Value"])
                if isinstance(row["Value"], str)
                else row["Value"]
            )
            condition += 1
        if row["Unit"].strip() != "-":
            U = row["Unit"]
            U = "percent" if U == "%" else U
            # U=ureg.parse_units(U)
            condition += 1
        if condition == 2:  # both value and unit are present
            try:
                Q = ureg(str(Val) + " " + str(U))
            except:  # conversion fail
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
        #print(f"{idx=}, {row=}")
        cList += [
            reagent(
                ID=str(row["Reagent ID"]),
                Chemical=chemical(
                    ID=row["Reagent ID"],
                    Name=row["Name"],
                    ChemicalFormula=row["Formula"],
                    MolarMass=assert_unit(row["Molar Mass"], "g/mol"),
                    Density=assert_unit(row["Density"], "g/cm^3"),
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
    #print(f"{value=}, {default_unit=}")
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


def find_reagent_in_rawmessage(
    searchString: str, reagentList: List[reagent]
) -> Optional[reagent]:
    """
    Returns (the first match of) a given reagent if its ID is found in an input string,
    otherwise returns None
    """
    for reag in reagentList:
        if reag.ID in searchString:
            return reag
    return None


def find_in_log(
    log: List[RawLogMessage],
    searchString: str,
    Highlander=True,  # there can be only one if Highlander is True
) -> Optional[Union[RawLogMessage, list[RawLogMessage]]]:
    """
    Returns (the first match of) a given reagent if its ID is found in an input string,
    otherwise returns None
    """
    answers = []
    for RLM in log:
        if searchString in RLM.Message:
            if Highlander:
                return RLM
            else:
                answers += [RLM]
    return answers
