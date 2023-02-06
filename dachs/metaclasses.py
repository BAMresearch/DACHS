#!/usr/bin/env python
# coding: utf-8

"""
Overview:
========
A dataclass for specifying metaclasses, superclasses that consist of collections of the end classes. 
experimentalSetup: a collection of equipment that make up an experimental setup.
"""

__author__ = "Brian R. Pauw"
__contact__ = "brian@stack.nl"
__license__ = "GPLv3+"
__date__ = "2022/11/15"
__status__ = "beta"

from attrs import define, validators, field
from typing import List, Optional
from additemstoattrs import addItemsToAttrs
from __init__ import ureg  # get importError when using: "from . import ureg"
import logging

from equipment import equipment


@define
class experimentalSetup(addItemsToAttrs):
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
    Description: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    EquipmentList: List[equipment] = field(
        default=None,
        validator=validators.instance_of(list),
        converter=list,
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
    eq1 = equipment(
        UID="BATH_1",
        Name="Lauda Bath",
        Manufacturer="Lauda",
        ModelName='Proline Edition X RP 855 C Cooling thermostat 230 V; 50 Hz',
        ModelNumber='L001603',
        UnitPrice="9756 euro",
        UnitSize="1 item",
        Description='funky bath with excellent temperature control'
    )

    su1 = experimentalSetup(
        UID="AMSET_6",
        Name="AutoMof Configuration 6",
        Description="Same as AMSET_4 but Rod shaped stirring bar",
        EquipmentList=[eq1]
    )

    print([f"{k}: {v}" for k, v in su1.items()])
    print(f"{su1._loadKeys=}")