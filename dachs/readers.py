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


from typing import List, Optional
from dachs.reagent import reagent
from dachs.synthesis import synthesisStep


def assert_unit(value, default_unit: str) -> str:
    """
    adds a default unit string for interpretation by pint
    if the value is not in string format yet
    (and therefore does not yet have a unit)
    """
    print(f"{value=}, {default_unit=}")
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
    Returns (the first match of) a given reagent if its UID is found in an input string,
    otherwise returns None
    """
    for reag in reagentList:
        if reag.UID in searchString:
            return reag
    return None
