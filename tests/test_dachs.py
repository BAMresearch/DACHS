import logging
from pathlib import Path
import sys
import pandas as pd
import pytest
import yaml
from dachs.__init__ import ureg
from dachs.equipment import Equipment, pv
from dachs.metaclasses import ExperimentalSetupClass, root
from dachs.readers import ReadStartingCompounds, readRawMessageLog
from dachs.reagent import (
    Mixture,
    Product,
    Reagent,
    Chemical,
)  # ReagentByMass, ReagentByVolume, ReagentMixture,

# from dachs.synthesis import RawLogMessage


def test_equipment() -> None:
    """Just a basic test of the class"""
    solvent = Equipment(
        ID="BATH_1",
        Name="Lauda Bath",
        Manufacturer="Lauda",
        ModelName="Proline Edition X RP 855 C Cooling thermostat 230 V; 50 Hz",
        ModelNumber="L001603",
        UnitPrice=ureg.Quantity("9756 euro"),
        UnitSize=ureg.Quantity("1 item"),
        Description="funky bath with excellent temperature control",
        PVs=[
            pv(
                ID="temp",
                Name="temperature",
                Description="Setpoint temperature of the bath",
                CalibrationFactor=1.0,
                CalibrationOffset="0 kelvin",
                Setpoint="20 kelvin",  # can also be set at a later stage, just wanted to check the units.
            )
        ],
    )
    e2 = Equipment(
        ID="VESS_1",
        Name="Falcon tube",
        Manufacturer="Labsolute",
        ModelName="Centrifuge Tube 50 ml, PP",
        ModelNumber="7696884",
        UnitPrice=ureg.Quantity("202 euro"),
        UnitSize=ureg.Quantity("300 items"),
        Description="Falcon tubes, 50 ml",
        PVs=[],
    )
    print([f"{k}: {v}" for k, v in solvent.items()])
    print(f"{solvent._loadKeys=}")
    # test ureg:
    print(e2.PricePerUnit())


def test_readEquipment() -> None:
    filename = Path("tests", "testData", "AutoMOFs_Logbook_Testing.xlsx")
    SetupName = "AMSET_6"

    # read equipment list:
    eq = pd.read_excel(filename, sheet_name="Equipment", index_col=None, header=0)
    eq = eq.dropna(how="all")
    eqDict = {}
    for rowi, equip in eq.iterrows():
        try:
            eqItem = Equipment(
                ID=str(equip["Equipment ID"]),
                Name=str(equip["Equipment Name"]),
                Manufacturer=str(equip["Manufacturer"]),
                ModelName=str(equip["Model Name"]),
                ModelNumber=str(equip["Model Number"]),
                UnitPrice=ureg.Quantity(str(equip["Unit Price"]) + " " + str(equip["Price Unit"])),
                UnitSize=ureg.Quantity(str(equip["Unit Size"]) + " " + str(equip["Unit"])),
                Description=str(equip["Description"]),
                PVs=[],
            )
            eqDict.update({str(equip["Equipment ID"]): eqItem})
        except Exception as e:
            print(f'Failure reading {equip["Equipment ID"]=}\n {str(e)}')

    # read setup configuration:
    df = pd.read_excel(filename, sheet_name="Setup", index_col=None, header=0)
    df = df.dropna(how="all")
    dfRow = df.loc[df.SetupID == SetupName].copy()
    assert len(dfRow == 1), f"More or less than one entry found for {SetupName=} in {filename=}"
    # get all equipment for the setup
    itemList = [dfRow[i].item() for i in dfRow.keys() if "ID_" in i]
    eqList = [eqDict[item] for item in itemList if item in eqDict.keys()]
    expSetup = ExperimentalSetupClass(
        ID=dfRow["SetupID"],
        Name=dfRow["Name"],
        Description=dfRow["Description"],
        EquipmentList=eqList,
    )
    print(filename)


def test_root() -> None:
    _ = root(
        ID="AutoMOF5",
        Name="Automatic MOF Exploration series 5",
        Description="""
            In this series, MOFs are synthesised in methanol from two stock solutions, 
            all performed at room temperature (see environmental details in log).
            The injection rate and injection order are varied. Centrifugation and drying 
            is performed manually. Residence times are 20 minutes after start of second injection.
        """,
    )
    return


def test_experimental_setup() -> None:
    """Just a basic test of the class"""
    eq1 = Equipment(
        ID="BATH_1",
        Name="Lauda Bath",
        Manufacturer="Lauda",
        ModelName="Proline Edition X RP 855 C Cooling thermostat 230 V; 50 Hz",
        ModelNumber="L001603",
        UnitPrice=ureg.Quantity("9756 euro"),
        UnitSize=ureg.Quantity("1 item"),
        Description="funky bath with excellent temperature control",
    )

    su1 = ExperimentalSetupClass(
        ID="AMSET_6",
        Name="AutoMof Configuration 6",
        Description="Same as AMSET_4 but Rod shaped stirring bar",
        EquipmentList=[eq1],
    )

    print([f"{k}: {v}" for k, v in su1.items()])
    print(f"{su1._loadKeys=}")


def test_readRawMessageLog() -> None:
    filename = Path("tests", "testData", "AutoMOFs05_H005.xlsx")
    _ = readRawMessageLog(filename)


def test_ReadStartingCompounds() -> None:
    filename = Path("tests", "testData", "AutoMOFs_Logbook_Testing.xlsx")
    _ = ReadStartingCompounds(filename)


def test_product() -> None:
    # define a zif Chemical:
    zifChemical = Chemical(
        ID="Zif-8",
        Name="Zif-8",
        ChemicalFormula="ZnSomething",
        MolarMass=ureg.Quantity("229 g/mol"),
        Density=ureg.Quantity("0.335 g/cc"),
        SourceDOI="something",
    )
    _ = Product(
        ID="ZIF-8", Chemical=zifChemical, Mass=ureg.Quantity("12.5 mg"), Purity="99 percent"
    )
    return


def test_reagent() -> None:
    """
    Tests for the Reagent class
    """
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    solvent = Reagent(
        ID="Solvent_1",
        Chemical=Chemical(
            ID="MeOH",
            Name="Methanol",
            ChemicalFormula="CH3OH",
            MolarMass=ureg.Quantity("32.04 g/mol"),
            Density=ureg.Quantity("0.79 g/ml"),
        ),
        CASNumber="67-56-1",
        Brand="Chemsolute",
        UNNumber="1230",
        MinimumPurity="98 percent",
        OpenDate="2022-05-01T10:04:22",
        StorageConditions=None,
        UnitPrice="9 euro",
        UnitSize="2.5 liter",
    )
    linker = Reagent(
        ID="linker_1",
        Chemical=Chemical(
            ID="2-MIM",
            Name="2-methylimidazole",
            ChemicalFormula="C4H6N2",
            MolarMass=ureg.Quantity("82.11 g/mol"),
            Density=ureg.Quantity("1.096 g/ml"),
        ),
        CASNumber="693-98-1",
        Brand="Sigma-Aldrich",
        UNNumber="3259",
        MinimumPurity="99 percent",
        OpenDate="2019-05-01T10:04:22",
        StorageConditions="air-conditioned lab",
        UnitPrice="149 euro",
        UnitSize="1000 gram",
    )

    print([f"{k}: {v}" for k, v in solvent.items()])
    print(f"{solvent._loadKeys=}")
    # test ureg:
    print(ureg("12.4 percent") * solvent.UnitPrice)
    print(solvent.PricePerUnit())

    # r1 = ReagentByVolume(
    #             AmountOfVolume='500 ml',
    #             Reagent=solvent
    #         )
    # r2 = ReagentByMass(
    #             AmountOfMass='4.5767 g',
    #             Reagent=linker
    #         )

    # make mixture:
    mixture = Mixture(
        ID="stock_1",
        Name="linker stock solution",
        Description="Stock solution of linker at 78 g/mole",
        PreparationDate="2022.07.27",
        StorageConditions="air conditioned lab",
        ComponentList=[solvent, linker],
        ComponentMasses=[ureg.Quantity("4.5767 g"), solvent.MassByVolume(ureg.Quantity("500 ml"))],
    )

    # print(f'{r1.Reagent.MolarMass=}')
    logging.info(
        [
            f"{c.MolesByMass(mixture.ComponentMasses[ci]):.3f} of {c.Chemical.Name} in"
            f" {mixture.Name} at mole concentration"
            f" {mixture.ComponentConcentration(MatchComponent=c):0.03e}"
            for ci, c in enumerate(mixture.ComponentList)
        ]
    )
    logging.info(
        [
            f"{c.PricePerMass():.3f} of {c.Chemical.Name} in {mixture.Name}"
            for c in mixture.ComponentList
        ]
    )
    logging.info(
        f"\n {mixture.ComponentConcentrations()=}, {mixture.TotalMass=}, {mixture.TotalPrice=}"
    )
