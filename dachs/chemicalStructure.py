#!/usr/bin/env python
# coding: utf-8

"""
Overview:
========
A dataclass for specifying a chemical structure.
"""

__author__ = "Brian R. Pauw"
__contact__ = "brian@stack.nl"
__license__ = "GPLv3+"
__date__ = "2022/11/15"
__status__ = "beta"

from attrs import define, validators, field
from typing import Optional
from additemstoattrs import addItemsToAttrs
from __init__ import ureg  # get importError when using: "from . import ureg"
import logging
from equipment import equipment


@define
class chemicalStructure(addItemsToAttrs):
    UID: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    Name: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    ChemicalFormula: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    MolarMass: float = field(
        default=None,
        validator=validators.instance_of(ureg.Quantity),
        converter=ureg,
    )
    Density: float = field(
        default=None,
        validator=validators.instance_of(ureg.Quantity),
        converter=ureg,
    )
    SourceDOI: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    # internals, don't need a lot of validation:
    _excludeKeys: list = ["_excludeKeys", "_storeKeys"]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing

    # def __attrs_post_init__(self):
    #     # auto-generate the store and load key lists:
    #     super().__attrs_post_init__()

if __name__ == "__main__":
    """Just a basic test of the class"""
    bath = equipment(
        UID="BATH_1",
        Name="Lauda Bath",
        Manufacturer="Lauda",
        ModelName='Proline Edition X RP 855 C Cooling thermostat 230 V; 50 Hz',
        ModelNumber='L001603',
        UnitPrice="9756 euro",
        UnitSize="1 item",
        Description='funky bath with excellent temperature control'
    )
    print([f"{k}: {v}" for k, v in bath.items()])
    print(f"{bath._loadKeys=}")
    # test ureg:
    print(bath.PricePerUnit())
