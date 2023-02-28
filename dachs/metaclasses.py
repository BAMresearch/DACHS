#!/usr/bin/env python
# coding: utf-8

"""
Overview:
========
A dataclass for specifying metaclasses, superclasses that consist of collections of the end classes. 
ExperimentalSetup: a collection of equipment that make up an experimental setup.
"""

__author__ = "Brian R. Pauw"
__contact__ = "brian@stack.nl"
__license__ = "GPLv3+"
__date__ = "2022/11/15"
__status__ = "beta"

from attrs import define, validators, field, Factory
from typing import List, Optional  # , Optional

from dachs.reagent import Chemical, Mixture, Product, Reagent # , ReagentMixture
from dachs.additemstoattrs import addItemsToAttrs

# from dachs.__init__ import ureg  # get importError when using: "from . import ureg"
# import logging
from dataclasses import dataclass
import dataclasses

from dachs.equipment import Equipment
from dachs.synthesis import SynthesisClass


@define
class ExperimentalSetupClass(addItemsToAttrs):
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
    Description: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    EquipmentList: List[Equipment] = field(
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


@define
class ChemicalsClass(addItemsToAttrs):
    starting_compounds: List[Reagent] = field(
        default=Factory(list),
        validator=validators.instance_of(list),
    )
    mixtures: List[Mixture] = field(
        default=Factory(list),
        validator=validators.instance_of(list),
    )
    final_product: Optional[Product] = field(  # probably could use an "evidence" too.
        default=None,
        validator=validators.optional(validators.instance_of(Product)),
    )
    target_product: Product = field(
        default=Factory(Product),
        validator=validators.instance_of(Product),
    )
    # internals, don't need a lot of validation:
    _excludeKeys: list = ["_excludeKeys", "_storeKeys"]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing


# @dataclass
# class ChemicalsClass:
#     starting_compounds: List = dataclasses.field(default_factory=list)
#     mixtures: List = dataclasses.field(default_factory=list)
#     final_product: Product = dataclasses.field(default_factory=Product)


@define
class root(addItemsToAttrs):
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
    Description: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    Chemicals: Optional[ChemicalsClass] = field(
        default=None,
        validator=validators.optional(validators.instance_of(ChemicalsClass)),
    )
    Synthesis: Optional[SynthesisClass] = field(
        default=None,
        validator=validators.optional(validators.instance_of(SynthesisClass)),
    )
    Characterizations: Optional[List] = field(
        default=None,
        validator=validators.optional(validators.instance_of(list)),
    )
    ExperimentalSetup: Optional[ExperimentalSetupClass] = field(
        default=None,
        validator=validators.optional(validators.instance_of(ExperimentalSetupClass)),
    )
    # internals, don't need a lot of validation:
    _excludeKeys: list = ["_excludeKeys", "_storeKeys"]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing
