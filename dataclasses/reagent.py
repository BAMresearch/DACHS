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
from addItemsToAttrs import addItemsToAttrs

# TODO: we probably need to add a units class like Pint


@define
class reagent(addItemsToAttrs):
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
        validator=validators.instance_of(float),
        converter=float,
    )
    Density: float = field(
        default=None,
        validator=validators.instance_of(float),
        converter=float,
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
        validator=validators.instance_of(float),
        converter=float,
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
        validator=validators.optional(validators.instance_of(float)),
        converter=float,
    )
    UnitSize: float = field(
        default=None,
        validator=validators.optional(validators.instance_of(float)),
        converter=float,
    )


if __name__ == "__main__":
    """Just a basic test of the class"""
    solvent = reagent(
        Name="Methanol",
        ChemicalFormula="MeOH",
        MolarMass=12.4,
        Density=0.8,
        CASNumber="1293847-2839147",
        Brand="Absolut",
        UNNumber="weori-198273",
        MinimumPurity=0.98,
        OpenDate="2022-05-01T10:04:22",
        StorageConditions=None,
        UnitPrice=12.4,
        UnitSize=1,
    )
    print([f"{k}: {v}" for k, v in solvent.items()])
