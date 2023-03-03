from datetime import datetime
import os
from pathlib import Path
import numpy as np
import pytest
import dachs as dachs
import logging
import sys

import chempy # we only need a tiny bit, but it does offer options...

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
    Chemical,
    Product,
    Reagent,
    Mixture
    # ReagentByMass,
    # ReagentByVolume,
    # ReagentMixture,
)
from dachs.metaclasses import root, ChemicalsClass
from dachs.synthesis import DerivedParameter, SynthesisClass, synthesisStep
from .__init__ import ureg  # get importError when using: "from . import ureg"


def test_integral() -> None:
    """
    Construction of a test structure from Glen's excel files using the available dataclasses,
    the hope is to use this as a template to construct the ontology, then write the structure to HDF5 files.
    It now defines:
        - base Chemicals and
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

    # define a zif Chemical:
    z8 = chempy.Substance.from_formula("ZnC8H12N4")
    zifChemical = Chemical(
        ID="Zif-8",
        Name="Zeolite Imidazole Framework type 8",
        ChemicalFormula="ZnC8H12N4",
        Substance=z8,
        MolarMass=ureg.Quantity(str(z8.molar_mass())),
        Density=ureg.Quantity("0.3 g/cc"),
        SourceDOI="something",
    )

    # Start with a root
    DACHS = root(
        ID="AutoMOF5",
        Name="Automatic MOF Exploration series 5",
        Description="""
            In this series, MOFs are synthesised in methanol from two stock solutions, 
            all performed at room temperature (see environmental details in log).
            The injection rate and injection order are varied. Centrifugation and drying 
            is performed manually. Residence times are ca. 20 minutes after start of second injection.
        """,
        Chemicals=ChemicalsClass(
            starting_compounds=ReadStartingCompounds(S0File),
            mixtures=[],
            target_product=Product(
                ID="ZIF-8", Chemical=zifChemical, Purity="99 percent"
            ),
            final_product=Product(
                ID="ZIF-8", Chemical=zifChemical, Purity="99 percent" # mass is set later. 
            ),
        ),
        ExperimentalSetup=readExperimentalSetup(
            filename = Path("tests", "testData", "AutoMOFs_Logbook_Testing.xlsx"),
            SetupName='AMSET_6'
        )
    )

    # logging.info("Defining the base chemicals / starting compounds")
    # DACHS.Chemicals.starting_compounds += 

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
        mix = Mixture(
                ID=solutionId,
                Name="Mixture",
                Description="",
                PreparationDate="TBD", # idx,  # last timestamp read
                StorageConditions="RT",
                # ComponentList=reagList,
                # Synthesis=None # will be filled in later
            )
        # now we find the Reagents that went into the mixture:
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
                    sstep.RawMessage, DACHS.Chemicals.starting_compounds
                )
                assert reag is not None, logging.warning(
                    f"Reagent not found in {sstep.RawMessage=}"
                )
                # print(f'{str(row["Value"]) + " " + str(row["Unit"])}, {reag.ID=}')
                mix.AddReagent(reag=reag, ReagentMass = ureg.Quantity(str(row["Value"]) + " " + str(row["Unit"])))
            synth += [sstep]
            stepId += 1
        # now we can define the mixture
        mix.PreparationDate=idx # last index found should be the date 
        mix.Synthesis = SynthesisClass(
                    ID=solutionId,
                    Name=f"Preparation of {solutionId}",
                    Description=" ",
                    SynthesisLog=synth,
                )
        DACHS.Chemicals.mixtures += [mix]
        # and we can add the synthesis used to make this mixture:
        print(f"{solutionId=}")

    logging.info(DACHS.Chemicals.mixtures)

    logging.info("defining the synthesis log")
    # just reading and dumping the synthesis log:
    filename = Path("tests", "testData", "AutoMOFs05_H005.xlsx")

    DACHS.Synthesis = SynthesisClass(
        ID="MOF_synthesis_1",
        Name="MOF standard synthesis, room temperature, 20 minute residence time",
        Description="-- add full text description of synthesis here--",
        RawLog=readRawMessageLog(filename),
    )

    #### After our discussion, we've decided not to focus on including derived parameters just yet. We still need a few things though. 
    logging.info("Extracting the derived parameters")
    # df = pd.read_excel(
    #     filename, sheet_name="Sheet1", index_col=None, header=0, parse_dates=["Time"]
    # )
    # df = df.dropna(how="all")

    # minimal derived information:
    # add the reaction mixtures to Chemicals.mixtures
    ## for the start time we need the last "start injection of solution" timestamp
    ReactionStart = find_in_log(
        DACHS.Synthesis.RawLog,
        "Start injection of solution",
        Highlander=True,
        Which='last'
        #return_indices=True,
    ).TimeStamp# .astimezone('UTC'))#, does this need str-ing?
    
    ## now we can create a new mixture
    mix = Mixture(
                ID="ReactionMix_0",
                Name="Reaction Mixture 0",
                Description="The MOF synthesis reaction mixture",
                PreparationDate=ReactionStart, # idx,  # last timestamp read
                StorageConditions="RT",
                Container=DACHS.ExperimentalSetup.EquipmentList[18]
            )
    ## to this we need to find the volume and density of which solution for the injections
    allVolumes=find_in_log(DACHS.Synthesis.RawLog, "Solution volume set", Highlander=False)
    assert len(allVolumes)!=0, 'No injection volume specified in log'
    assert len(allVolumes)==1, 'More than one injection volumes specified in log, dissimilar solution volumes not yet implemented'
    VolumeRLM=allVolumes[0]
    allSolutions=find_in_log(DACHS.Synthesis.RawLog, 'Stop injection of solution', Highlander=False)
    # I don't have the densities yet, so we have to assume something for now
    for solutionRLM in allSolutions:
        solutionId = solutionRLM.Value
        mix.AddMixture(
            DACHS.Chemicals.mixtures[solutionId],
            AddMixtureVolume=VolumeRLM.Quantity, # TODO: correction factor should be added in 
            MixtureDensity=ureg.Quantity('0.792 g/cc'), # TODO: methanol density for now
        )
    # Add to the structure. 
    DACHS.Chemicals.mixtures += [mix]

    # # calculate the weight of Product:
    WeightRLMs=find_in_log(DACHS.Synthesis.RawLog, ['Weight', 'Falcon'], Highlander=False)
    # targets = ["Weight", "Falcon"]
    # # find me the messages containing both those words:
    # dfMask = df["Readout"].apply(
    #     lambda sentence: all(word in sentence for word in targets)
    # )
    # mLocs = np.where(dfMask)[0]
    assert len(WeightRLMs) == 2, 'more than two weight indications (empty, empty+dry product) were found'
    DACHS.Chemicals.final_product.Mass = WeightRLMs[1].Quantity - WeightRLMs[0].Quantity
    # compute theoretical yield:
    # we need to find out how many moles of metal we have in the previously established reaction mixture
    for component in mix.ComponentList:
        aNumber = chempy.util.periodic.atomic_number("Zn")
        if aNumber in component.Chemical.Substance.composition.keys():
            # this is the component we're looking for. How many moles of atoms per moles of substance?
            metalMoles = component.Chemical.Substance.composition[aNumber]
            TotalMetalMoles = mix.ComponentMoles(MatchComponent=component) * metalMoles
        if 'C4H6N2' in component.Chemical.Substance.name:
            TotalLinkerMoles = mix.ComponentMoles(MatchComponent=component)

    DACHS.Synthesis.ExtraInformation.update({'MetalToLinkerRatio': TotalMetalMoles/TotalLinkerMoles})
    DACHS.Chemicals.target_product.Mass=TotalMetalMoles * DACHS.Chemicals.target_product.Chemical.MolarMass
    print(DACHS.Chemicals.ChemicalYield)
    DACHS.Chemicals._storeKeys += ['ChemicalYield']
    # maybe later
    # DACHS.Synthesis.ChemicalReaction = chempy.Reaction.from_string("")
    DACHS.Synthesis.SourceDOI = "10.1039/D1RA02856A"


    # DACHS.Chemicals.target_product.Mass = 

    # DerivedParameter(
    #     Name="Yield",
    #     Description="Actual yield of the Product",
    #     RawMessages=list(mLocs),
    #     Quantity=DACHS.Synthesis.RawLog[mLocs[-1]].Quantity
    #     - DACHS.Synthesis.RawLog[mLocs[0]].Quantity,
    # )

    # # store the room temperature:
    # LogEntry = find_in_log(
    #     DACHS.Synthesis.RawLog,
    #     "arduino:environment:temperature",
    #     Highlander=True,
    #     #return_indices=True,
    # )
    # DACHS.Synthesis.DerivedParameters += [
    #     DerivedParameter(
    #         Name="RoomTemperature",
    #         Description="Actual room temperature at synthesis time",
    #         RawMessages=[LogEntry.Index],
    #         Quantity=LogEntry.Quantity,
    #     )
    # ]

    # Export everything finally
    from dachs.serialization import storagePaths
    name = 'DACHS'
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
            McHDF.storeKV(filename=f'{name}_H005.h5', path=key, value=value)
        except Exception:
            print(f"Error for path {key} and value '{value}' of type {type(value)}.")
            raise