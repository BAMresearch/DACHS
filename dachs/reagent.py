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

    ID: str = field(
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
    SourceDOI: Optional[str] = field(
        default=None,
        validator=validators.optional(validators.instance_of(str)),
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

    ID: str = field(
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
    ID: str = field(
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

    # @property
    def _CheckForPriceCalc(self):
        assert (self.Chemical.Density is not None) and (self.UnitPrice is not None) and (
            self.UnitSize is not None
        ), logging.warning(
            "Price calculations can only be done when UnitSize and UnitPrice as well as Chemical.Density are set"
        )
        return

    # @property
    def PricePerUnit(self) -> ureg.Quantity:
        self._CheckForPriceCalc()
        return self.UnitPrice / self.UnitSize

    # @property
    def PricePerMass(self) -> Union[ureg.Quantity, None] :
        self._CheckForPriceCalc()
        if self.UnitSize.check('[mass]'): return self.PricePerUnit()
        elif self.UnitSize.check('[volume]'):
            return self.PricePerUnit() / self.Chemical.Density
        else: 
            logging.warning(f'Price per mass cannot be calculated from {self.PricePerUnit=}')
            return None

    # @property
    def PricePerVolume(self) -> Union[ureg.Quantity, None] :
        self._CheckForPriceCalc()
        if self.UnitSize.check('[volume]'): return self.PricePerUnit()
        elif self.UnitSize.check('[mass]'):
            return self.PricePerUnit() * self.Chemical.Density
        else: 
            logging.warning(f'Price per volume cannot be calculated from {self.PricePerUnit=}')
            return None


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

    # @property
    def componentConcentration(self, componentID: str) -> float:
        """
        Finds the concentration of a component defined by its componentID in the total mixture
        This concentration will be in mole fraction.
        """
        componentMoles = 0
        totalMoles = 0
        for component in self.ReagentList:
            totalMoles += component.Moles()
            if component.Reagent.ID == componentID:
                componentMoles = component.Moles()
        if componentMoles == 0:
            logging.warning(
                f"Concentration of component {componentID} is zero, component not found"
            )
        return componentMoles / totalMoles
