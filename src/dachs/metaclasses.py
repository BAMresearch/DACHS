#!/usr/bin/env python
# coding: utf-8

"""
A dataclass for specifying metaclasses, superclasses that consist of collections of the end classes.
ExperimentalSetup: a collection of equipment that make up an experimental setup.
"""

__author__ = "Brian R. Pauw"
__contact__ = "brian@stack.nl"
__license__ = "GPLv3+"
__date__ = "2022/11/15"
__status__ = "beta"

import logging

# import logging
from typing import List, Optional  # , Optional

from attrs import Factory, define, field, validators

from dachs import ureg  # get importError when using: "from . import ureg"
from dachs.additemstoattrs import addItemsToAttrs
from dachs.equipment import Equipment
from dachs.reagent import Mixture, Product, Reagent  # , ReagentMixture
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
class EnvironmentClass(addItemsToAttrs):
    """Calss for storing environmental parameters including stirring speed"""

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
    Temperature: Optional[ureg.Quantity] = field(
        default=None,
        validator=validators.instance_of(ureg.Quantity),
        converter=ureg.Quantity,
    )
    Humidity: Optional[ureg.Quantity] = field(
        default=None,
        validator=validators.instance_of(ureg.Quantity),
        converter=ureg.Quantity,
    )
    Pressure: Optional[ureg.Quantity] = field(
        default=None,
        validator=validators.instance_of(ureg.Quantity),
        converter=ureg.Quantity,
    )
    # internals, don't need a lot of validation:
    _excludeKeys: list = ["_excludeKeys", "_storeKeys"]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing


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

    @property
    def ChemicalYield(self):
        assert (self.target_product.Mass is not None) and (self.final_product.Mass is not None), logging.warning(
            "Yield can only be calculated when both target mass and actual mass are set"
        )
        assert self.target_product.Chemical == self.final_product.Chemical, logging.warning(
            "Yield can only be calculated when target and final Chemicals are the same "
        )
        # maybe not a required assertion:
        # assert self.target_product.Mass > self.final_product.Mass, logging.warning(
        #     "target (ideal) mass has to be bigger than final product mass"
        # )
        return self.final_product.Mass / self.target_product.Mass


# @define
# class DocumentationClass(addItemsToAttrs):
#     RoboticSetup = field(
#         default=None,
#     )
#     ChemicalReaction = field(
#         default=None,
#     )


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
    # Documentation: Optional[DocumentationClass] = field(
    #     default=None,
    #     validator=validators.optional(validators.instance_of(DocumentationClass)),
    # )
    # internals, don't need a lot of validation:
    _excludeKeys: list = ["_excludeKeys", "_storeKeys"]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing
