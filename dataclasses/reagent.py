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
from typing import List, Optional
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

    def Moles(self)->float:
        return self.AmountOfMass / self.Reagent.MolarMass

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
    def Moles(self)->float:
        return self.AmountOfVolume * self.Reagent.Density / self.Reagent.MolarMass

@define
class reagentMixture(addItemsToAttrs):
    '''
    Defines chemicals prepared for the experiments from the reagents from the shelves. 
    '''
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
    ReagentList: List = field( # list of reagentByMass and/or reagentByVolume
        default=None,
        validator=validators.instance_of(list),
        converter=list,
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
    # internals, don't need a lot of validation:
    _excludeKeys: list = ["_excludeKeys", "_storeKeys"]  # exclude from HDF storage
    _storeKeys: list = []  # store these keys (will be filled in later)
    _loadKeys: list = []  # load these keys from file if reconstructing


if __name__ == "__main__":
    """Just a basic test of the class"""
    solvent = reagent(
        UID="Solvent_1",
        Name="Methanol",
        ChemicalFormula="CH3OH",
        MolarMass="32.04 g/mol",
        Density="0.79 g/ml",
        CASNumber="67-56-1",
        Brand="Chemsolute",
        UNNumber="1230",
        MinimumPurity="98 percent",
        OpenDate="2022-05-01T10:04:22",
        StorageConditions=None,
        UnitPrice="9 euro",
        UnitSize="2.5 liter",
    )
    linker = reagent(
        UID="linker_1",
        Name="2-methylimidazole",
        ChemicalFormula="C4H6N2",
        MolarMass="82.11 g/mol",
        Density="1.096 g/ml",
        CASNumber="693-98-1",
        Brand="Sigma-Aldrich",
        UNNumber="3259",
        MinimumPurity="99 percent",
        OpenDate="2019-05-01T10:04:22",
        StorageConditions='air-conditioned lab',
        UnitPrice="149 euro",
        UnitSize="1000 gram",
    )

    print([f"{k}: {v}" for k, v in solvent.items()])
    print(f"{solvent._loadKeys=}")
    # test ureg:
    print(ureg("12.4 percent")* solvent.UnitPrice)
    print(solvent.PricePerUnit())

    r1 = reagentByVolume(
                AmountOfVolume='500 ml',
                Reagent=solvent
            )
    # make mixture: 
    mixture = reagentMixture(
        UID='stock_1',
        Name='linker stock solution',
        Description='Stock solution of linker at 78 g/mole',
        PreparationDate='2022.07.27',
        StorageConditions='air conditioned lab',
        ReagentList=[
            r1,
            reagentByMass(
                AmountOfMass='4.5767 g',
                Reagent=linker
            )
        ]
    )
    print(f'{r1.Reagent.MolarMass=}')
    print([f'{m.Moles()} of {m.Reagent.Name} in {mixture.Name}' for m in mixture.ReagentList])