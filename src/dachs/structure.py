import logging
import os
import sys
from pathlib import Path
from typing import List

import chempy  # we only need a tiny bit, but it does offer options...
import pandas as pd

from dachs import ureg
from dachs.metaclasses import ChemicalsClass, Experiment
from dachs.readers import (
    ReadStartingCompounds,
    find_in_log,
    find_reagent_in_rawmessage,
    find_trigger_in_log,
    readExperimentalSetup,
    readRawMessageLog,
)
from dachs.reagent import Mixture  # ReagentByMass,; ReagentByVolume,; ReagentMixture,
from dachs.reagent import Chemical, Product
from dachs.synthesis import SynthesisClass, synthesisStep


def create(logFile: Path, solFiles: List[Path], synFile: Path, amset: str = None) -> Experiment:
    """
    Construction of a test structure from Glen's excel files using the available dataclasses,
    the hope is to use this as a template to construct the ontology, then write the structure to HDF5 files.

    It now defines:
        - base Chemicals and
        - mixtures

    **TODO**:
        - write synthesis log
        - write or (perhaps better) link to SAS data structure.
        - write or (perhaps better) link to analysis results?

    :param logFile: Path to the robot log book Excel file
    :param solFiles: One or more Excel files describing the base solutions which were mixed by the robot
    :param synFile: The synthesis robot log file.
    """
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.info(f"Working in '{os.getcwd()}'.")

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

    # Start with a Experiment
    exp = Experiment(
        ID="DACHS", # this also defines the root at which the HDF5 tree starts
        Name="Automatic MOF Exploration series",
        Description="""
            In this series, MOFs are synthesised in methanol from two stock solutions,
            all performed at room temperature (see environmental details in log).
            The injection rate and injection order are varied. Centrifugation and drying
            is performed manually. Residence times are ca. 20 minutes after start of second injection.
        """,
        Chemicals=ChemicalsClass(
            starting_compounds=ReadStartingCompounds(logFile),
            mixtures=[],
            target_product=Product(ID="ZIF-8", Chemical=zifChemical, Purity="99 percent"),
            final_product=Product(ID="ZIF-8", Chemical=zifChemical, Purity="99 percent"),  # mass is set later.
        ),
        ExperimentalSetup=readExperimentalSetup(filename=logFile, SetupName=amset),
    )

    logging.info("defining the mixtures based on mixtures of starting compounds")

    # make a mixture as defined in each of the excel sheets:
    for filename in solFiles:
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
        synth = []
        mix = Mixture(
            ID=solutionId,
            Name="Mixture",
            Description="",
            PreparationDate=pd.to_datetime('1980-12-31'),  # idx,  # will be replaced with last timestamp read
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
                TimeStamp=pd.to_datetime(row["Time"]),
                stepDescription="Generating stock solutions",
                stepType="mixing",
                ExperimentId=row["ExperimentID"],
            )
            if find_trigger_in_log(sstep, triggerList=["mass of"]): # find_trigger_in_log(sstep, triggerList=["Weight"]) or 
                # we found a component to add to the mixture
                reag = find_reagent_in_rawmessage(sstep.RawMessage, exp.Chemicals.starting_compounds)
                if reag is not None: # logging.warning(f"Reagent not found in {sstep.RawMessage=}")
                    # print(f'{str(row["Value"]) + " " + str(row["Unit"])}, {reag.ID=}')
                    mix.AddReagent(reag=reag, ReagentMass=ureg.Quantity(str(row["Value"]) + " " + str(row["Unit"])))
            if find_trigger_in_log(sstep, triggerList=["mixed together"]): # in the one log, it's "Solutions mixed together", in the other "Solution components mixed together"...S
                mix.PreparationDate=sstep.TimeStamp
            synth += [sstep]
            stepId += 1
        # now we can define the mixture
        # mix.PreparationDate = find_in_log(
        #     synth,
        #     "Solutions mixed together",
        #     Highlander=True,
        #     Which="last"
        #     # return_indices=True,
        #     ).TimeStamp  # last index found should be the date
        mix.Synthesis = SynthesisClass(
            ID=solutionId,
            Name=f"Preparation of {solutionId}",
            Description=" ",
            SynthesisLog=synth,
        )
        exp.Chemicals.mixtures += [mix]
        # and we can add the synthesis used to make this mixture:
        print(f"{solutionId=}")

    # logging.info(exp.Chemicals.mixtures)

    logging.info("defining the synthesis log")

    exp.Synthesis = SynthesisClass(
        ID="MOF_synthesis_1",
        Name="MOF standard synthesis in MeOH, room temperature, nominally 20 minute residence time",
        Description=r"""
            note: these are nominal conditions for the series, but variations in injection quantities, speeds,
            reaction times, temperatures and post-processing have been applied. For exact conditions for this
            particular synthesis, please consult the log and metadata.

            ZIF-8 (Zinc Imidazole Framework-8) was synthesised from two stock solutions,
            the first consisting of zinc nitrate hexahydrate in methanol (MeOH), and the second consisting
            of 2-Methylimidazole (2-MeIm) in MeOH. 10 ml of each stock solution was injected into a falcon
            tube, at a rate up to 20 ml/min, and stirred at 200 rpm for normally 20 minutes at an ambient
            laboratory temperature of around 25$^{\circ}$C.
            This resulted in a final synthesis of Zn: 2-MeIm: MeOH molar ratio as specified in the synthesis
            concentration list.
            After the allowed synthesis time, the reaction mixture was centrifuged at 6000 rpm for 20 minutes,
            and subsequently dried at 60$^{\circ}$C for 22 hours.

        """,
        RawLog=readRawMessageLog(synFile),
    )

    # After our discussion, we've decided not to focus on including derived parameters just yet.
    # We still need a few things though.
    logging.info("Extracting the derived parameters")
    # df = pd.read_excel(
    #     filename, sheet_name="Sheet1", index_col=None, header=0, parse_dates=["Time"]
    # )
    # df = df.dropna(how="all")

    # minimal derived information:
    # add the reaction mixtures to Chemicals.mixtures
    # for the start time we need the last "start injection of solution" timestamp
    ReactionStart = find_in_log(
        exp.Synthesis.RawLog,
        "Start injection of solution",
        Highlander=True,
        Which="last"
        # return_indices=True,
    ).TimeStamp  # .astimezone('UTC'))#, does this need str-ing?

    ReactionStop = find_in_log(
        exp.Synthesis.RawLog,
        "Sample placed in centrifuge",
        Highlander=True,
        Which="last"
        # return_indices=True,
    ).TimeStamp  # .astimezone('UTC'))#, does this need str-ing?

    exp.Synthesis.ExtraInformation.update(
        {"ReactionTime": ureg.Quantity((ReactionStop - ReactionStart).total_seconds(), "s")}
    )

    if amset is not None:
        sun = amset
    else:
        LogEntry = find_in_log(
            exp.Synthesis.RawLog,
            "SetupID",
            Highlander=True,
            Which="last",
            # return_indices=True,
        )
        if LogEntry == []:
            logging.error("No AMSET configuration found in log, but also not specified as input argument.")
            raise SyntaxError

        if 'AMSET' in LogEntry.Value:
            sun = LogEntry.Value
        else:
            logging.error("No AMSET configuration found in log, but also not specified as input argument.")
            raise SyntaxError

    # At this point, we need the experimental setup as we need the falcon tube..
    exp.ExperimentalSetup = readExperimentalSetup(filename=logFile, SetupName=sun)

    # now we can create a new mixture
    mix = Mixture(
        ID="ReactionMix_0",
        Name="Reaction Mixture 0",
        Description="The MOF synthesis reaction mixture",
        PreparationDate=ReactionStart,  # idx,  # last timestamp read
        StorageConditions="RT",
        Container=[i for i in exp.ExperimentalSetup.EquipmentList if "falcon tube" in i.Name.lower()][-1],
    )
    # to this we need to find the volume and density of which solution for the injections
    allVolumes = find_in_log(exp.Synthesis.RawLog, "Solution volume set", Highlander=False)
    assert len(allVolumes) != 0, "No injection volume specified in log"
    # assert (
    #     len(allVolumes) == 1
    # ), "More than one injection volumes specified in log, dissimilar solution volumes not yet implemented"
    
    # find calibration factor and offset:
    Syringe=[i for i in exp.ExperimentalSetup.EquipmentList if i.Name.lower()=='syringe'][-1]
    CalibrationFactor=Syringe.CalibrationFactor
    CalibrationOffset=Syringe.CalibrationOffset
    allSolutions = find_in_log(exp.Synthesis.RawLog, ["Stop", "injection of solution"], Highlander=False)
    # I don't have the densities yet, so we have to assume something for now
    for solutionRLM in allSolutions:
        solutionId = solutionRLM.Value
        # figure out which volume was used for this by looking at the index:
        for volRLM in allVolumes:
            if volRLM.Index < solutionRLM.Index: # the last time we set the volume before injection is the volume used. 
                VolumeRLM=volRLM

        # VolumeRLM = allVolumes[0]
        mix.AddMixture(
            exp.Chemicals.mixtures[solutionId],
            AddMixtureVolume=VolumeRLM.Quantity * CalibrationFactor
            + CalibrationOffset,  # TODO: correction factor should be added in
            MixtureDensity=ureg.Quantity("0.792 g/cc"),  # TODO: methanol density for now
        )
    # Add to the structure.
    exp.Chemicals.mixtures += [mix]

    # calculate the age of solution0 and solution1 into the mix:
    exp.Synthesis.ExtraInformation.update(
        {"MetalSolutionAge": ureg.Quantity((exp.Chemicals.mixtures[2].PreparationDate - exp.Chemicals.mixtures[0].PreparationDate).total_seconds(), "s")}
    )
    exp.Synthesis.ExtraInformation.update(
        {"LinkerSolutionAge": ureg.Quantity((exp.Chemicals.mixtures[2].PreparationDate - exp.Chemicals.mixtures[1].PreparationDate).total_seconds(), "s")}
    )

    # calculate the weight of Product:
    InitialWeight = find_in_log(exp.Synthesis.RawLog, ["empty Falcon tube"], excludeString=['+ dry sample', ' lid'], Highlander=True, Which='last')
    FinalWeight = find_in_log(exp.Synthesis.RawLog, ["of Falcon tube + dry sample"], excludeString=['lid'], Highlander=True, Which='last')

    # WeightRLMs = find_in_log(exp.Synthesis.RawLog, ["Weight", "Falcon"], Highlander=False)
    # targets = ["Weight", "Falcon"]
    # # find me the messages containing both those words:
    # dfMask = df["Readout"].apply(
    #     lambda sentence: all(word in sentence for word in targets)
    # )
    # mLocs = np.where(dfMask)[0]
    logging.debug(f' {InitialWeight=}, \n {FinalWeight=}')
    # assert len(WeightRLMs) == 2, "more than two weight indications (empty, empty+dry product) were found"
    # exp.Chemicals.final_product.Mass = WeightRLMs[1].Quantity - WeightRLMs[0].Quantity
    exp.Chemicals.final_product.Mass = FinalWeight.Quantity - InitialWeight.Quantity
    # compute theoretical yield:
    # we need to find out how many moles of metal we have in the previously established reaction mixture
    logging.debug(f'{len(mix.ComponentList)=}')
    for component in mix.ComponentList:
        aNumber = chempy.util.periodic.atomic_number("Zn")
        logging.debug(f'{component.Chemical.Substance.composition.keys()=}')
        if aNumber in component.Chemical.Substance.composition.keys():
            # this is the component we're looking for. How many moles of atoms per moles of substance?
            metalMoles = component.Chemical.Substance.composition[aNumber]
            TotalMetalMoles = mix.ComponentMoles(MatchComponent=component) * metalMoles
        if "C4H6N2" in component.Chemical.Substance.name:
            TotalLinkerMoles = mix.ComponentMoles(MatchComponent=component)
        if "CH3OH" in component.Chemical.Substance.name:
            TotalMethanolMoles = mix.ComponentMoles(MatchComponent=component)

    exp.Synthesis.ExtraInformation.update({"MetalToLinkerRatio": TotalMetalMoles / TotalLinkerMoles})
    exp.Synthesis.ExtraInformation.update({"MetalToMethanolRatio": TotalMetalMoles / TotalMethanolMoles})

    exp.Chemicals.target_product.Mass = TotalMetalMoles * exp.Chemicals.target_product.Chemical.MolarMass
    logging.debug(f"{exp.Chemicals.ChemicalYield=}")
    exp.Chemicals._storeKeys += ["ChemicalYield"]
    # maybe later
    # exp.Synthesis.ChemicalReaction = chempy.Reaction.from_string("")
    exp.Synthesis.SourceDOI = "10.1039/D1RA02856A"

    # exp.Chemicals.target_product.Mass =

    # DerivedParameter(
    #     Name="Yield",
    #     Description="Actual yield of the Product",
    #     RawMessages=list(mLocs),
    #     Quantity=exp.Synthesis.RawLog[mLocs[-1]].Quantity
    #     - exp.Synthesis.RawLog[mLocs[0]].Quantity,
    # )

    # store the room temperature:
    LogEntry = find_in_log(
        exp.Synthesis.RawLog,
        "arduino:environment:temperature",
        Highlander=True,
        Which="last",
        # return_indices=True,
    )
    exp.Synthesis.ExtraInformation.update({"LabTemperature": LogEntry.Quantity})
    # injection speed:
    LogEntry = find_in_log(
        exp.Synthesis.RawLog,
        "Solution rate set",
        Highlander=True,
        Which="last",
        # return_indices=True,
    )
    exp.Synthesis.ExtraInformation.update({"InjectionSpeed": LogEntry.Quantity})

    # exp.Synthesis.DerivedParameters += [
    #     DerivedParameter(
    #         Name="RoomTemperature",
    #         Description="Actual room temperature at synthesis time",
    #         RawMessages=[LogEntry.Index],
    #         Quantity=LogEntry.Quantity,
    #     )
    # ]

    # lastly, we can remove all the unused reagents from starting_compounds:
    exp.Chemicals.starting_compounds = [item for item in exp.Chemicals.starting_compounds if item.Used]

    return exp
