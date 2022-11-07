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

from attrs import define, validators, field, cmp_using, fields
from typing import List, Optional, Any, NoReturn
from collections.abc import Iterable

# TODO: we probably need to add a units class like Pint
@define
class reagent:
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
