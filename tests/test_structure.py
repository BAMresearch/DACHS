from datetime import datetime
import os
from pathlib import Path
import numpy as np
import pytest
import dachs as dachs
import logging
import sys

import pandas as pd
from dachs.readers import (
    ReadStartingCompounds,
    assert_unit,
    find_in_log,
    find_reagent_in_rawmessage,
    find_trigger_in_log,
    readExperimentalSetup,
    readRawMessageLog,
)
from dachs.reagent import (
    chemical,
    product,
    reagent,
    reagentByMass,
    reagentByVolume,
    reagentMixture,
)
from dachs.metaclasses import root, chemicals
from dachs.synthesis import DerivedParameter, synthesis, synthesisStep


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
        ID="Zif-8",
        Name="Zif-8",
        ChemicalFormula="ZnC8H12N4",
        MolarMass="229.6 g/mol",
        Density="0.3 g/cc",
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
            is performed manually. Residence times are ca. 20 minutes after start of second injection.
        """,
        Chemicals=chemicals(
            starting_compounds=ReadStartingCompounds(S0File),
            mixtures=[],
            target_product=product(
                ID="ZIF-8", Chemical=zifChemical, Mass="12.5 mg", Purity="99 percent"
            ),
            final_product=product(
                ID="ZIF-8", Chemical=zifChemical, Mass="10.8 mg", Purity="99 percent"
            ),
        ),
        ExperimentalSetup=readExperimentalSetup(
            filename = Path("tests", "testData", "AutoMOFs_Logbook_Testing.xlsx"),
            SetupName='AMSET_6'
        )
    )

    # logging.info("Defining the base chemicals / starting compounds")
    # rootStruct.Chemicals.starting_compounds += 

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
            filename,
            sheet_name="Sheet1",
            index_col=None,
            header=0,
            parse_dates=["Time"],
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
                ID=str(stepId),
                RawMessage=row["Readout"],
                RawMessageLevel=row["Info"],
                TimeStamp=row["Time"],
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
                # print(f'{str(row["Value"]) + " " + str(row["Unit"])}, {reag.ID=}')
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
                ID=solutionId,
                Name="Mixture",
                Description="",
                PreparationDate=idx,  # last timestamp read
                StorageConditions="",
                ReagentList=reagList,
                Synthesis=synthesis(
                    ID=solutionId,
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

    rootStruct.Synthesis = synthesis(
        ID="MOF_synthesis_1",
        Name="MOF standard synthesis, room temperature, 20 minute residence time",
        Description="-- add full text description of synthesis here--",
        RawLog=readRawMessageLog(filename),
    )

    #     filename = Path("tests", "testData", "AutoMOFs_Logbook_Testing.xlsx")
    # SetupName='AMSET_6'
    # rootStruct.ExperimentalSetup=readExperimentalSetup(
    #     filename = Path("tests", "testData", "AutoMOFs_Logbook_Testing.xlsx"),
    #     SetupName='AMSET_6'
    # )

    #### After our discussion, we've decided not to focus on including derived parameters just yet. 
    # logging.info("Extracting the derived parameters")
    # df = pd.read_excel(
    #     filename, sheet_name="Sheet1", index_col=None, header=0, parse_dates=["Time"]
    # )
    # df = df.dropna(how="all")

    # # calculate the weight of product:
    # targets = ["Weight", "Falcon"]
    # # find me the messages containing both those words:
    # dfMask = df["Readout"].apply(
    #     lambda sentence: all(word in sentence for word in targets)
    # )
    # mLocs = np.where(dfMask)[0]
    # assert len(mLocs) == 2
    # rootStruct.Synthesis.DerivedParameters = [
    #     DerivedParameter(
    #         Name="Yield",
    #         Description="Actual yield of the product",
    #         RawMessages=list(mLocs),
    #         Quantity=rootStruct.Synthesis.RawLog[mLocs[-1]].Quantity
    #         - rootStruct.Synthesis.RawLog[mLocs[0]].Quantity,
    #     )
    # ]

    # # store the room temperature:
    # LogEntry = find_in_log(
    #     rootStruct.Synthesis.RawLog,
    #     "arduino:environment:temperature",
    #     Highlander=True,
    #     #return_indices=True,
    # )
    # rootStruct.Synthesis.DerivedParameters += [
    #     DerivedParameter(
    #         Name="RoomTemperature",
    #         Description="Actual room temperature at synthesis time",
    #         RawMessages=[LogEntry.Index],
    #         Quantity=LogEntry.Quantity,
    #     )
    # ]

    # Export everything finally
    from dachs.serialization import storagePaths
    name = 'rootStruct'
    dump = storagePaths(name, locals()[name])

    # quick&dirty imports for testing
    # make sure mcsas3 is in PYTHONPATH (for now)
    mcsas3Path = Path('../mcsas3').resolve()
    if mcsas3Path not in sys.path:
        sys.path.insert(0, str(mcsas3Path))
    #print(sys.path)
    import mcsas3.McHDF as McHDF

    # locate any warnings during processing
    import warnings
    #warnings.filterwarnings("error")

    for key, value in dump.items():
        # extracting path from keys could be added to McHDF.storeKVPairs()
        try:
            McHDF.storeKV(filename=f'{name}.h5', path=key, value=value)
        except Exception:
            print(f"Error for path {key} and value '{value}' of type {type(value)}.")
            raise