#!/usr/bin/env python
# coding: utf-8

"""
A dataclass for specifying a generic piece of equipment.
"""

__author__ = "Brian R. Pauw"
__contact__ = "brian@stack.nl"
__license__ = "GPLv3+"
__date__ = "2022/11/15"
__status__ = "beta"

from attrs import define, validators, field, Factory
from typing import List, Optional
from .additemstoattrs import addItemsToAttrs
from .__init__ import ureg  # get importError when using: "from . import ureg"
import logging


@define
class pv(addItemsToAttrs):
    """
    A process variable which can be added to a piece of equipment.
    Each process variable has a calibration factor and calibration offset as well.
    These link the actual output with the set value as follows:
    PV_real = PV_set * calibrationFactor + calibrationOffset
    """

    ID: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    Name: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    Setpoint: float = field(
        default=None,
        validator=validators.instance_of(ureg.Quantity),
        converter=ureg,
    )
    Actual: float = field(
        default=None,
        validator=validators.instance_of(ureg.Quantity),
        converter=ureg,
    )
    Description: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    CalibrationFactor: float = field(
        default=1.0,
        validator=validators.instance_of(float),  # unitless
        converter=float,
    )
    CalibrationOffset: float = field(
        default="0.0 kelvin",
        validator=validators.instance_of(ureg.Quantity),
        converter=ureg,
    )
    # internals, don't need a lot of validation:
    _excludeKeys: list = ["_excludeKeys", "_storeKeys"]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing
    # value=Setpoint # straightforward for now

    # def __attrs_post_init__(self):
    #     # auto-generate the store and load key lists:
    #     super().__attrs_post_init__()


@define
class Equipment(addItemsToAttrs):
    ID: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    Name: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    Manufacturer: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    ModelName: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    ModelNumber: Optional[str] = field(
        default=None,
        validator=validators.optional(validators.instance_of(str)),
        converter=str,
    )
    Description: Optional[str] = field(
        default=None,
        validator=validators.optional(validators.instance_of(str)),
        converter=str,
    )
    UnitPrice: Optional[ureg.Quantity] = field(
        default=None,
        validator=validators.optional(validators.instance_of(ureg.Quantity)),
    )
    UnitSize: Optional[ureg.Quantity] = field(
        default=None,
        validator=validators.optional(validators.instance_of(ureg.Quantity)),
    )
    PVs: List[pv] = field(
        default=Factory(list),
        validator=validators.instance_of(list),
    )
    AlternativeIDs: List[str] = field(
        default=Factory(list),
        validator=validators.instance_of(list),
    )
    # internals, don't need a lot of validation:
    _excludeKeys: list = ["_excludeKeys", "_storeKeys"]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing

    # def __attrs_post_init__(self):
    #     # auto-generate the store and load key lists:
    #     super().__attrs_post_init__()

    def PricePerUnit(self):
        assert (self.UnitPrice is not None) and (
            self.UnitSize is not None
        ), logging.warning(
            "PricePerUnit can only be calculated when both UnitSize and UnitPrice are set"
        )
        return self.UnitPrice / self.UnitSize
