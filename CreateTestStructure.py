#!/usr/bin/env python
# coding: utf-8

"""
Overview:
========
Construction of a test structure from Glen's excel files using the dataclasses here. 

"""

__author__ = "Brian R. Pauw"
__contact__ = "brian@stack.nl"
__license__ = "GPLv3+"
__date__ = "2022/11/07"
__status__ = "beta"

from dataclasses import dataclass
from pathlib import Path
from dachs.reagent import reagent, reagentByMass, reagentByVolume, reagentMixture

@dataclass
class root():
    """Root entry point for the structure"""
    ID=''
    name=''
    description=''
    starting_compounds=[]
    synthesis=[]
    final_product=[]
    characterizations=[]


if __name__=='__main__': 
    S0File = Path('testData', 'AutoMOFs_Logbook_Testing.xlsx')
    assert S0File.exists()
    