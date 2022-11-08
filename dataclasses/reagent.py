#!/usr/bin/env python
# coding: utf-8

"""
Overview:
========
A dataclass for specifying a reagent.
"""

__author__ = "Brian R. Pauw"
__contact__ = "brian@stack.nl"
__license__ = "GPLv3+"
__date__ = "2022/11/07"
__status__ = "beta"

from attrs import define, validators, field
from typing import Optional
from additemstoattrs import addItemsToAttrs
from __init__ import ureg  # get importError when using: "from . import ureg"
import logging

# from dachsvalidators import isQuantity


@define
class reagent(addItemsToAttrs):
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
    CASNumber: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    Brand: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    UNNumber: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    MinimumPurity: float = field(
        default=None,
        validator=validators.instance_of(ureg.Quantity),
        converter=ureg,
    )
    OpenDate: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    StorageConditions: Optional[str] = field(
        default=None,
        validator=validators.optional(validators.instance_of(str)),
        converter=str,
    )
    UnitPrice: Optional[float] = field(
        default=None,
        validator=validators.instance_of(ureg.Quantity),
        converter=ureg,
    )
    UnitSize: float = field(
        default=None,
        validator=validators.instance_of(ureg.Quantity),
        converter=ureg,
    )
    # internals, don't need a lot of validation:
    _excludeKeys: list = ["_excludeKeys", "_storeKeys"]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing

    def __attrs_post_init__(self):
        # auto-generate the store and load key lists:
        self._storeKeys = [
            i
            for i in self.keys()
            if (i not in self._excludeKeys and not i.startswith("_"))
        ]
        self._loadKeys = [
            i
            for i in self.keys()
            if (i not in self._excludeKeys and not i.startswith("_"))
        ]

    def PricePerUnit(self):
        assert (self.UnitPrice is not None) and (
            self.UnitSize is not None
        ), logging.warning(
            "PricePerUnit can only be calculated when both UnitSize and UnitPrice are set"
        )
        return self.UnitPrice / self.UnitSize


if __name__ == "__main__":
    """Just a basic test of the class"""
    solvent = reagent(
        UID="Solvent_1",
        Name="Methanol",
        ChemicalFormula="MeOH",
        MolarMass="12.4 g/mol",
        Density="0.8 g/cc",
        CASNumber="1293847-2839147",
        Brand="Absolut",
        UNNumber="weori-198273",
        MinimumPurity="98 percent",
        OpenDate="2022-05-01T10:04:22",
        StorageConditions=None,
        UnitPrice="12.4 euro",
        UnitSize="0.5 liter",
    )
    print([f"{k}: {v}" for k, v in solvent.items()])
    print(f"{solvent._loadKeys=}")
    # test ureg:
    print(ureg("12.4 microliter"))
    print(solvent.PricePerUnit())
