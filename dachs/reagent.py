#!/usr/bin/env python
# coding: utf-8

"""
Overview:
========
A dataclass for specifying a reagent, reagentmixture or product.
"""

__author__ = "Brian R. Pauw"
__contact__ = "brian@stack.nl"
__license__ = "GPLv3+"
__date__ = "2022/11/07"
__status__ = "beta"

from attrs import define, validators, field, Factory
from typing import List, Optional, Union

from dachs.synthesis import synthesis

from .additemstoattrs import addItemsToAttrs
from .__init__ import ureg  # get importError when using: "from . import ureg"
import logging

# from dachsvalidators import isQuantity


@define
class chemical(addItemsToAttrs):
    """Base chemistry which underpins both reagents and products"""

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


@define
class product(addItemsToAttrs):
    """
    Defines a chemical product as having a chemical structure, with a target mass (100% conversion) and an actual mass
    """

    UID: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    Chemical: chemical = field(
        default=None,
        validator=validators.instance_of(chemical),
        # converter=reagent,
    )
    Mass: float = field(
        default=None,
        validator=validators.instance_of(ureg.Quantity),
        converter=ureg,
    )
    Purity: Optional[float] = field(
        default=None,
        validator=validators.optional(validators.instance_of(ureg.Quantity)),
        converter=ureg,
    )
    _excludeKeys: list = [
        "_excludeKeys",
        "_storeKeys",
        "chemicalYield",
    ]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing

    def chemicalYield(self):
        assert (self.ActualMass is not None) and (
            self.TargetMass is not None
        ), logging.warning(
            "Yied can only be calculated when both target mass and actual mass are set"
        )
        assert self.TargetMass > self.ActualMass, logging.warning(
            "target mass has to be bigger than actual mass"
        )
        return self.ActualMass / self.TargetMass


@define
class reagent(addItemsToAttrs):
    UID: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    Chemical: chemical = field(
        default=None,
        validator=validators.instance_of(chemical),
        # converter=reagent,
    )
    # Name and the following are in chemical
    # ChemicalFormula: str = field(
    #     default=None,
    #     validator=validators.instance_of(str),
    #     converter=str,
    # )
    # MolarMass: float = field(
    #     default=None,
    #     validator=validators.instance_of(ureg.Quantity),
    #     converter=ureg,
    # )
    # Density: float = field(
    #     default=None,
    #     validator=validators.instance_of(ureg.Quantity),
    #     converter=ureg,
    # )
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

    def PricePerUnit(self):
        assert (self.UnitPrice is not None) and (
            self.UnitSize is not None
        ), logging.warning(
            "PricePerUnit can only be calculated when both UnitSize and UnitPrice are set"
        )
        return self.UnitPrice / self.UnitSize


@define
class reagentByMass(addItemsToAttrs):
    AmountOfMass: float = field(
        default=None,
        validator=validators.instance_of(ureg.Quantity),
        converter=ureg,
    )
    Reagent: reagent = field(
        default=None,
        validator=validators.instance_of(reagent),
        # converter=reagent,
    )

    # internals, don't need a lot of validation:
    _excludeKeys: list = ["_excludeKeys", "_storeKeys"]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing

    def Moles(self) -> float:
        return self.AmountOfMass / self.Reagent.Chemical.MolarMass


@define
class reagentByVolume(addItemsToAttrs):
    AmountOfVolume: float = field(
        default=None,
        validator=validators.instance_of(ureg.Quantity),
        converter=ureg,
    )
    Reagent: reagent = field(
        default=None,
        validator=validators.instance_of(reagent),
        # converter=reagent,
    )
    # internals, don't need a lot of validation:
    _excludeKeys: list = ["_excludeKeys", "_storeKeys"]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing

    def Moles(self) -> float:
        return (
            self.AmountOfVolume
            * self.Reagent.Chemical.Density
            / self.Reagent.Chemical.MolarMass
        )


@define
class reagentMixture(addItemsToAttrs):
    """
    Defines chemicals prepared for the experiments from the reagents from the shelves.
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
    Description: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    ReagentList: List[
        Union[reagentByMass, reagentByVolume]
    ] = field(  # list of reagentByMass and/or reagentByVolume
        default=Factory(list),
        validator=validators.instance_of(list),
    )
    PreparationDate: str = field(
        default=None,
        validator=validators.instance_of(str),
        converter=str,
    )
    StorageConditions: Optional[str] = field(
        default=None,
        validator=validators.optional(validators.instance_of(str)),
        converter=str,
    )
    Synthesis: Optional[synthesis] = field(
        default=None,
        validator=validators.optional(validators.instance_of(synthesis)),
    )
    # internals, don't need a lot of validation:
    _excludeKeys: list = ["_excludeKeys", "_storeKeys"]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing

    def componentConcentration(self, componentID: str) -> float:
        """
        Finds the concentration of a component defined by its componentID in the total mixture
        This concentration will be in mole fraction.
        """
        componentMoles = 0
        totalMoles = 0
        for component in self.ReagentList:
            totalMoles += component.Moles()
            if component.Reagent.UID == componentID:
                componentMoles = component.Moles()
        if componentMoles == 0:
            logging.warning(
                f"Concentration of component {componentID} is zero, component not found"
            )
        return componentMoles / totalMoles
