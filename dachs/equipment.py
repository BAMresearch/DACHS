#!/usr/bin/env python
# coding: utf-8

"""
Overview:
========
A dataclass for specifying a generic piece of equipment.
"""

__author__ = "Brian R. Pauw"
__contact__ = "brian@stack.nl"
__license__ = "GPLv3+"
__date__ = "2022/11/15"
__status__ = "beta"

from attrs import define, validators, field
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
class equipment(addItemsToAttrs):
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
    ModelNumber: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    Description: str = field(
        default=None,
        validator=validators.instance_of(str),
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
    PVs: List[pv] = field(
        default=[],
        validator=validators.instance_of(list),
        converter=list,
    )
    AlternativeIDs: List[str] = field(
        default=[],
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

    def PricePerUnit(self):
        assert (self.UnitPrice is not None) and (
            self.UnitSize is not None
        ), logging.warning(
            "PricePerUnit can only be calculated when both UnitSize and UnitPrice are set"
        )
        return self.UnitPrice / self.UnitSize


if __name__ == "__main__":
    """Just a basic test of the class"""
    solvent = equipment(
        UID="BATH_1",
        Name="Lauda Bath",
        Manufacturer="Lauda",
        ModelName="Proline Edition X RP 855 C Cooling thermostat 230 V; 50 Hz",
        ModelNumber="L001603",
        UnitPrice="9756 euro",
        UnitSize="1 item",
        Description="funky bath with excellent temperature control",
        PVs=[
            pv(
                UID="temp",
                Name="temperature",
                Description="Setpoint temperature of the bath",
                CalibrationFactor=1.0,
                CalibrationOffset="0 kelvin",
                Setpoint="20 kelvin",  # can also be set at a later stage, just wanted to check the units.
            )
        ],
    )
    e2 = equipment(
        UID="VESS_1",
        Name="Falcon tube",
        Manufacturer="Labsolute",
        ModelName="Centrifuge Tube 50 ml, PP",
        ModelNumber="7696884",
        UnitPrice="202 euro",
        UnitSize="300 items",
        Description="Falcon tubes, 50 ml",
        PVs=[],
    )
    print([f"{k}: {v}" for k, v in solvent.items()])
    print(f"{solvent._loadKeys=}")
    # test ureg:
    print(e2.PricePerUnit())
