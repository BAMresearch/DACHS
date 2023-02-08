from datetime import datetime
import os
from pathlib import Path
import pytest
import dachs as dachs
import logging
import sys

import pandas as pd
from dachs.readers import assert_unit, find_reagent_in_rawmessage, find_trigger_in_log
from dachs.reagent import (
    chemical,
    product,
    reagent,
    reagentByMass,
    reagentByVolume,
    reagentMixture,
)
from dachs.metaclasses import root, chemicals
from dachs.synthesis import synthesis, synthesisStep


def test_integral() -> None:
    """
    Construction of a test structure from Glen's excel files using the available dataclasses,
    the hope is to use this as a template to construct the ontology, then write the structure to HDF5 files.
    It now defines:
        - base chemicals and
        - mixtures,
    todo:
        - write synthesis log
        - write or (perhaps better) link to SAS data structure.
        - write or (perhaps better) link to analysis results?
    """
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    # Input excel sheet, containing all necessary information:
    logging.info(f"{os.getcwd()}")
    S0File = Path("tests", "testData", "AutoMOFs_Logbook_Testing.xlsx")
    assert S0File.exists()

    # define a zif chemical:
    zifChemical = chemical(
        Name="Zif-8",
        ChemicalFormula="ZnSomething",
        MolarMass="12.5 g/mol",
        Density="0.335 g/cc",
        SourceDOI="something",
    )

    # Start with a root
    rootStruct = root(
        ID="AutoMOF5",
        Name="Automatic MOF Exploration series 5",
        Description="""
            In this series, MOFs are synthesised in methanol from two stock solutions, 
            all performed at room temperature (see environmental details in log).
            The injection rate and injection order are varied. Centrifugation and drying 
            is performed manually. Residence times are 20 minutes after start of second injection.
        """,
        Chemicals=chemicals(
            starting_compounds=[],
            mixtures=[],
            target_product=product(
                UID="ZIF-8", Chemical=zifChemical, Mass="12.5 mg", Purity="99 percent"
            ),
            final_product=product(
                UID="ZIF-8", Chemical=zifChemical, Mass="10.8 mg", Purity="99 percent"
            ),
        ),
    )

    logging.info("Defining the base chemicals / starting compounds")
    df = pd.read_excel(
        S0File, sheet_name="Chemicals", index_col=0, header=0, parse_dates=["Open Date"]
    )
    df = df.dropna(how="all")
    # Turn the specified chemicals into a list of starting compounds
    for idx, row in df.iterrows():
        print(f"{idx=}, {row=}")
        rootStruct.Chemicals.starting_compounds += [
            reagent(
                UID=str(idx),
                Chemical=chemical(
                    Name=row["Name"],
                    ChemicalFormula=row["Formula"],
                    MolarMass=assert_unit(row["Molar Mass"], "g/mol"),
                    Density=assert_unit(row["Density"], "g/cm^3"),
                ),
                CASNumber=row["CAS-Number"],
                Brand=row["Brand"],
                UNNumber=row["UN-Number"],
                MinimumPurity=assert_unit(row["Purity"], "percent"),
                OpenDate=row["Open Date"],
                StorageConditions=row["Storage Conditions"],
                UnitPrice=assert_unit(row["Unit Price"], "euro"),
                UnitSize=assert_unit(row["Unit Size"], row["Unit"]),
            )
        ]
    # print(rootStruct.chemicals.starting_compounds)

    logging.info("defining the mixtures based on mixtures of starting componds")
    filenames = [
        Path("tests", "testData", "AutoMOFs05_Solution0.xlsx"),
        Path("tests", "testData", "AutoMOFs05_Solution1.xlsx"),
    ]
    # make a mixture as defined in each of the excel sheets:
    for filename in filenames:
        assert filename.exists(), f"{filename=} does not exist"
        # read the synthesis logs:
        df = pd.read_excel(
            filename, sheet_name="Sheet1", index_col=0, header=0, parse_dates=["Time"]
        )
        stepId = 1
        assert len(df.SampleNumber.unique()) == 1, logging.error(
            "no unique mixture ID (sampleNumber) identified in the solution log"
        )
        solutionId = df.SampleNumber.unique()[0]
        reagList = []
        synth = []
        # now we find the reagents that went into the mixture:
        for idx, row in df.iterrows():
            sstep = synthesisStep(
                UID=str(stepId),
                RawMessage=row["Readout"],
                RawMessageLevel=row["Info"],
                TimeStamp=idx,
                stepDescription="Generating stock solutions",
                stepType="mixing",
                ExperimentId=row["ExperimentID"],
            )
            if find_trigger_in_log(sstep, triggerList=["Weight"]):
                # we found a component to add to the mixture
                reag = find_reagent_in_rawmessage(
                    sstep.RawMessage, rootStruct.Chemicals.starting_compounds
                )
                assert reag is not None, logging.warning(
                    f"reagent not found in {sstep.RawMessage=}"
                )
                # print(f'{str(row["Value"]) + " " + str(row["Unit"])}, {reag.UID=}')
                reagList += [
                    reagentByMass(
                        Reagent=reag,
                        AmountOfMass=str(row["Value"]) + " " + str(row["Unit"]),
                    )
                ]
            synth += [sstep]
            stepId += 1
        # now we can define the mixture
        rootStruct.Chemicals.mixtures += [
            reagentMixture(
                UID=solutionId,
                Name="Mixture",
                Description="",
                PreparationDate=idx,  # last timestamp read
                StorageConditions="",
                ReagentList=reagList,
                Synthesis=synthesis(
                    UID=solutionId,
                    Name=f"Preparation of {solutionId}",
                    Description=" ",
                    SynthesisLog=synth,
                ),
            )
        ]
        # and we can add the synthesis used to make this mixture:
        print(f"{solutionId=}")

    logging.info(rootStruct.Chemicals.mixtures)

    logging.info("defining the synthesis log")
    # just reading and dumping the synthesis log:
    filename = Path("tests", "testData", "AutoMOFs05_H005.xlsx")
    assert filename.exists()
    df = pd.read_excel(
        filename, sheet_name="Sheet1", index_col=None, header=0, parse_dates=["Time"]
    )
    for idx, row in df.iterrows():
        pass
    logging.info("defining the synthesis steps (nicely organized from log)")
