import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import chempy  # we only need a tiny bit, but it does offer options...
import numpy as np
import pandas as pd
import pytest

import dachs as dachs
from dachs.metaclasses import ChemicalsClass, root
from dachs.readers import (
    ReadStartingCompounds,
    assert_unit,
    find_in_log,
    find_reagent_in_rawmessage,
    find_trigger_in_log,
    readExperimentalSetup,
    readRawMessageLog,
)
from dachs.reagent import Mixture  # ReagentByMass,; ReagentByVolume,; ReagentMixture,
from dachs.reagent import Chemical, Product, Reagent
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
            target_product=Product(ID="ZIF-8", Chemical=zifChemical, Purity="99 percent"),
            final_product=Product(ID="ZIF-8", Chemical=zifChemical, Purity="99 percent"),  # mass is set later.
        ),
        ExperimentalSetup=readExperimentalSetup(
            filename=Path("tests", "testData", "AutoMOFs_Logbook_Testing.xlsx"), SetupName="AMSET_6"
        ),
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
            PreparationDate="TBD",  # idx,  # last timestamp read
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
                reag = find_reagent_in_rawmessage(sstep.RawMessage, DACHS.Chemicals.starting_compounds)
                assert reag is not None, logging.warning(f"Reagent not found in {sstep.RawMessage=}")
                # print(f'{str(row["Value"]) + " " + str(row["Unit"])}, {reag.ID=}')
                mix.AddReagent(reag=reag, ReagentMass=ureg.Quantity(str(row["Value"]) + " " + str(row["Unit"])))
            synth += [sstep]
            stepId += 1
        # now we can define the mixture
        mix.PreparationDate = idx  # last index found should be the date
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
        Name="MOF standard synthesis in MeOH, room temperature, nominally 20 minute residence time",
        Description="""
            note: these are nominal conditions for the series, but variations in injection quantities, speeds,
            reaction times, temperatures and post-processing have been applied. For exact conditions for this particular synthesis,
            please consult the log and metadata.

            ZIF-8 (Zinc Imidazole Framework-8) was synthesised from two stock solutions,
            the first consisting of zinc nitrate hexahydrate in methanol (MeOH), and the second consisting
            of 2-Methylimidazole (2-MeIm) in MeOH. 10 ml of each stock solution was injected into a falcon
            tube, at a rate up to 20 ml/min, and stirred at 200 rpm for normally 20 minutes at an ambient
            laboratory temperature of around 25$^{\circ}$C.
            This resulted in a final synthesis of Zn: 2-MeIm: MeOH molar ratio as specified in the synthesis concentration list.
            After the allowed synthesis time, the reaction mixture was centrifuged at 6000 rpm for 20 minutes,
            and subsequently dried at 60$^{\circ}$C for 22 hours.

        """,
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
        Which="last"
        # return_indices=True,
    ).TimeStamp  # .astimezone('UTC'))#, does this need str-ing?

    ReactionStop = find_in_log(
        DACHS.Synthesis.RawLog,
        "Sample placed in centrifuge",
        Highlander=True,
        Which="last"
        # return_indices=True,
    ).TimeStamp  # .astimezone('UTC'))#, does this need str-ing?

    DACHS.Synthesis.ExtraInformation.update(
        {"ReactionTime": ureg.Quantity((ReactionStop - ReactionStart).total_seconds(), "s")}
    )

    ## now we can create a new mixture
    mix = Mixture(
        ID="ReactionMix_0",
        Name="Reaction Mixture 0",
        Description="The MOF synthesis reaction mixture",
        PreparationDate=ReactionStart,  # idx,  # last timestamp read
        StorageConditions="RT",
        Container=[i for i in DACHS.ExperimentalSetup.EquipmentList if "falcon tube" in i.Name.lower()][-1],
    )
    ## to this we need to find the volume and density of which solution for the injections
    allVolumes = find_in_log(DACHS.Synthesis.RawLog, "Solution volume set", Highlander=False)
    assert len(allVolumes) != 0, "No injection volume specified in log"
    assert (
        len(allVolumes) == 1
    ), "More than one injection volumes specified in log, dissimilar solution volumes not yet implemented"
    VolumeRLM = allVolumes[0]
    allSolutions = find_in_log(DACHS.Synthesis.RawLog, "Stop injection of solution", Highlander=False)
    # I don't have the densities yet, so we have to assume something for now
    for solutionRLM in allSolutions:
        solutionId = solutionRLM.Value
        mix.AddMixture(
            DACHS.Chemicals.mixtures[solutionId],
            AddMixtureVolume=VolumeRLM.Quantity,  # TODO: correction factor should be added in
            MixtureDensity=ureg.Quantity("0.792 g/cc"),  # TODO: methanol density for now
        )
    # Add to the structure.
    DACHS.Chemicals.mixtures += [mix]

    # # calculate the weight of Product:
    WeightRLMs = find_in_log(DACHS.Synthesis.RawLog, ["Weight", "Falcon"], Highlander=False)
    # targets = ["Weight", "Falcon"]
    # # find me the messages containing both those words:
    # dfMask = df["Readout"].apply(
    #     lambda sentence: all(word in sentence for word in targets)
    # )
    # mLocs = np.where(dfMask)[0]
    assert len(WeightRLMs) == 2, "more than two weight indications (empty, empty+dry product) were found"
    DACHS.Chemicals.final_product.Mass = WeightRLMs[1].Quantity - WeightRLMs[0].Quantity
    # compute theoretical yield:
    # we need to find out how many moles of metal we have in the previously established reaction mixture
    for component in mix.ComponentList:
        aNumber = chempy.util.periodic.atomic_number("Zn")
        if aNumber in component.Chemical.Substance.composition.keys():
            # this is the component we're looking for. How many moles of atoms per moles of substance?
            metalMoles = component.Chemical.Substance.composition[aNumber]
            TotalMetalMoles = mix.ComponentMoles(MatchComponent=component) * metalMoles
        if "C4H6N2" in component.Chemical.Substance.name:
            TotalLinkerMoles = mix.ComponentMoles(MatchComponent=component)
        if "CH3OH" in component.Chemical.Substance.name:
            TotalMethanolMoles = mix.ComponentMoles(MatchComponent=component)

    DACHS.Synthesis.ExtraInformation.update({"MetalToLinkerRatio": TotalMetalMoles / TotalLinkerMoles})
    DACHS.Synthesis.ExtraInformation.update({"MetalToMethanolRatio": TotalMetalMoles / TotalMethanolMoles})

    DACHS.Chemicals.target_product.Mass = TotalMetalMoles * DACHS.Chemicals.target_product.Chemical.MolarMass
    print(DACHS.Chemicals.ChemicalYield)
    DACHS.Chemicals._storeKeys += ["ChemicalYield"]
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

    # store the room temperature:
    LogEntry = find_in_log(
        DACHS.Synthesis.RawLog,
        "arduino:environment:temperature",
        Highlander=True,
        Which="last",
        # return_indices=True,
    )
    DACHS.Synthesis.ExtraInformation.update({"LabTemperature": LogEntry.Quantity})
    # injection speed:
    LogEntry = find_in_log(
        DACHS.Synthesis.RawLog,
        "Solution rate set",
        Highlander=True,
        Which="last",
        # return_indices=True,
    )
    DACHS.Synthesis.ExtraInformation.update({"InjectionSpeed": LogEntry.Quantity})

    # DACHS.Synthesis.DerivedParameters += [
    #     DerivedParameter(
    #         Name="RoomTemperature",
    #         Description="Actual room temperature at synthesis time",
    #         RawMessages=[LogEntry.Index],
    #         Quantity=LogEntry.Quantity,
    #     )
    # ]

    # lastly, we can remove all the unused reagents from starting_compounds:
    DACHS.Chemicals.starting_compounds = [item for item in DACHS.Chemicals.starting_compounds if item.Used]

    # Export everything finally
    from dachs.serialization import storagePaths

    name = "DACHS"
    dump = storagePaths(name, locals()[name])

    # quick&dirty imports for testing
    # make sure mcsas3 is in PYTHONPATH (for now)
    mcsas3Path = Path("../mcsas3").resolve()
    if mcsas3Path not in sys.path:
        sys.path.insert(0, str(mcsas3Path))
    # print(sys.path)
    # locate any warnings during processing
    import warnings

    import mcsas3.McHDF as McHDF

    # warnings.filterwarnings("error")

    for key, value in dump.items():
        # extracting path from keys could be added to McHDF.storeKVPairs()
        try:
            McHDF.storeKV(filename=f"{name}_H005.h5", path=key, value=value)
        except Exception:
            print(f"Error for path {key} and value '{value}' of type {type(value)}.")
            raise
