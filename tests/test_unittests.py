import logging
import sys
import pytest
from dachs.__init__ import ureg
from dachs.equipment import equipment, pv
from dachs.metaclasses import experimentalSetup, root
from dachs.reagent import product, reagent, reagentByMass, reagentByVolume, reagentMixture, chemical

def test_equipment()->None:
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


def test_root()->None:
    _=root(
        ID='AutoMOF5',
        Name='Automatic MOF Exploration series 5',
        Description="""
            In this series, MOFs are synthesised in methanol from two stock solutions, 
            all performed at room temperature (see environmental details in log).
            The injection rate and injection order are varied. Centrifugation and drying 
            is performed manually. Residence times are 20 minutes after start of second injection.
        """
    )
    return


def test_experimental_setup()->None:
    """Just a basic test of the class"""
    eq1 = equipment(
        UID="BATH_1",
        Name="Lauda Bath",
        Manufacturer="Lauda",
        ModelName="Proline Edition X RP 855 C Cooling thermostat 230 V; 50 Hz",
        ModelNumber="L001603",
        UnitPrice="9756 euro",
        UnitSize="1 item",
        Description="funky bath with excellent temperature control",
    )

    su1 = experimentalSetup(
        UID="AMSET_6",
        Name="AutoMof Configuration 6",
        Description="Same as AMSET_4 but Rod shaped stirring bar",
        EquipmentList=[eq1],
    )

    print([f"{k}: {v}" for k, v in su1.items()])
    print(f"{su1._loadKeys=}")


def test_product()->None:
    # define a zif chemical:
    zifChemical = chemical(
            Name='Zif-8',
            ChemicalFormula="ZnSomething",
            MolarMass="12.5 g/mol",
            Density="0.335 g/cc",
            SourceDOI="something",
    )
    _=product(
                UID="ZIF-8", Chemical=zifChemical, Mass="12.5 mg", Purity="99 percent"
            )
    return


def test_reagent()->None:
    """
    Tests for the reagent class
    """
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    solvent = reagent(
        UID="Solvent_1",
        Chemical=chemical(
            Name="Methanol",
            ChemicalFormula="CH3OH",
            MolarMass="32.04 g/mol",
            Density="0.79 g/ml",
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
    linker = reagent(
        UID="linker_1",
        Chemical=chemical(
            Name="2-methylimidazole",
            ChemicalFormula="C4H6N2",
            MolarMass="82.11 g/mol",
            Density="1.096 g/ml",
        ),
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
    r2 = reagentByMass(
                AmountOfMass='4.5767 g',
                Reagent=linker
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
            r2
        ]
    )
    # print(f'{r1.Reagent.MolarMass=}')
    logging.info([f'{m.Moles():.3f} of {m.Reagent.Chemical.Name} in {mixture.Name} at mole concentration {mixture.componentConcentration(componentID=m.Reagent.UID):0.03e}' for m in mixture.ReagentList])