#!/usr/bin/env python
# coding: utf-8

"""
Overview:
========
A dataclass for describing a synthesis
"""

__author__ = "Brian R. Pauw"
__contact__ = "brian@stack.nl"
__license__ = "GPLv3+"
__date__ = "2022/11/07"
__status__ = "beta"

from attrs import define, validators, field, Factory
from typing import List, Optional
from .additemstoattrs import addItemsToAttrs
from .__init__ import ureg  # get importError when using: "from . import ureg"
import logging
from .equipment import pv


@define
class synthesisStep(addItemsToAttrs):
    UID: str = field(  # step number
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    RawMessage: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    RawMessageLevel: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    TimeStamp: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    stepType: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    stepDescription: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    EquipmentId: Optional[str] = field(
        default=Factory(str),
        validator=validators.optional(validators.instance_of(str)),
        # converter=str,
    )
    PVs: Optional[pv] = field(
        default=Factory(pv),
        validator=validators.optional(validators.instance_of(pv)),
        # converter=pv,
    )
    ExperimentId: Optional[str] = field(
        default=Factory(str),
        validator=validators.optional(validators.instance_of(str)),
        # converter=str,
    )
    SampleId: Optional[str] = field(
        default=Factory(str),
        validator=validators.optional(validators.instance_of(str)),
        # converter=str,
    )
    _excludeKeys: list = ["_excludeKeys", "_storeKeys"]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing


@define
class synthesis(addItemsToAttrs):
    UID: str = field(  # step number
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
    SynthesisLog: List[synthesisStep] = field(
        default=None,
        validator=validators.instance_of(list),
        converter=list,
    )
    SourceDOI: Optional[str] = field(
        default=Factory(str),
        validator=validators.optional(validators.instance_of(str)),
        # converter=str,
    )
    DerivedParameters: Optional[dict] = field(
        default=Factory(dict),
        validator=validators.optional(validators.instance_of(dict)),
        # converter=dict,
    )
    _excludeKeys: list = ["_excludeKeys", "_storeKeys"]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing
