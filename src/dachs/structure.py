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
from dachs.synthesis import DerivedParameter, SynthesisClass, synthesisStep


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

    # define a ZIF 8 Chemical, we'll need this later:
    z8 = chempy.Substance.from_formula("C8H10N4Zn")
    zifChemical = Chemical(
        ID="ZIF-8",
        ChemicalName="Zeolitic Imidazolate Framework 8",
        ChemicalFormula="C8H10N4Zn",
        Substance=z8,
        MolarMass=ureg.Quantity(str(z8.molar_mass())),
        Density=ureg.Quantity("0.9426 g/cc"),
        SourceDOI="10.1038/s42004-021-00613-z",
        SpaceGroup="I-43m",
    )

    # define a ZIF L Chemical, we'll need these later too:
    zl = chempy.Substance.from_formula("C24H38N12O3Zn2")
    zifLChemical = Chemical(
        ID="ZIF-L",
        ChemicalName="Zeolitic Imidazolate Framework L",
        ChemicalFormula="C24H38N12O3Zn2",
        Substance=zl,
        MolarMass=ureg.Quantity(str(zl.molar_mass())),
        Density=ureg.Quantity("1.4042 g/cc"),
        SourceDOI="10.1038/s42004-021-00613-z",
        SpaceGroup="Cmca",
    )

    # Start with a Experiment
    exp = Experiment(
        ID="DACHS",  # this also defines the root at which the HDF5 tree starts
        Name="Automatic MOF Exploration series",
        Description="""
            In this series, MOFs are synthesised in methanol from two stock solutions,
            all performed at room temperature (see environmental details in log).
            The injection rate and injection order are varied. Centrifugation and drying
            is performed manually. Residence times are ca. 20 minutes after start of second injection.
        """,
        # in this experiment, we are going to use some chemicals. These are defined by the chemicals class.
        Chemicals=ChemicalsClass(
            # There is a list of starting compounds in the log file
            starting_compounds=ReadStartingCompounds(logFile),
            mixtures=[],  # mixtures get filled in later
            # Then we have the potential products from the synthesis. Be as thorough as you like here, it will help you later on
            potential_products=[
                Product(ID="ZIF-8", Chemical=zifChemical),
                Product(ID="ZIF-L", Chemical=zifLChemical),
            ],
            # the target product is what you are aiming to get:
            target_product=Product(ID="target_product", Chemical=zifChemical),
            # the final product is what you actually got in the end, as evidenced by the evidence.
            final_product=Product(
                ID="final_product", Chemical=zifChemical, Evidence="Assumed for now ¯\_(ツ)_/¯"
            ),  # mass is set later.
        ),
        # We're usin this experimental set-up for this experiment.
        # TODO: read the setupname from the AMSET note in the logs. The experimental setup can be defined later, so we'll probably shift this down to after we determined it.
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
        assert len(df.SampleNumber.unique()) == 1, logging.error(
            "no unique mixture ID (sampleNumber) identified in the solution log"
        )
        solutionId = df.SampleNumber.unique()[0]
        rawLog = readRawMessageLog(filename)
        mix = Mixture(
            ID=solutionId,
            MixtureName="Mixture",
            Description="",
            PreparationDate=pd.to_datetime("1980-12-31"),  # idx,  # will be replaced with last timestamp read
            StorageConditions="RT",
            # ComponentList=reagList,
            # Synthesis=None # will be filled in later
        )

        # new style 20230919, attempting to get rid of synthesisStep
        aNumber = chempy.util.periodic.atomic_number("Zn")
        mixIsMetal = False
        mixIsLinker = False
        for reagent in exp.Chemicals.starting_compounds:
            RLMList = find_in_log(rawLog, [reagent.ID, "mass of"], Highlander=False)
            if len(RLMList) != 0:  # if the list is not empty:
                for RLM in RLMList:  # add each to the mix
                    mix.AddReagent(reag=reagent, ReagentMass=RLM.Quantity)
                    if aNumber in reagent.Chemical.Substance.composition.keys():
                        mixIsMetal = True
                    if "C4H6N2" in reagent.Chemical.Substance.name:
                        mixIsLinker = True

        if mixIsMetal:
            mix.Description = "Metal salt dispersion"
        if mixIsLinker:
            mix.Description = "Organic linker dispersion"

        RLM = find_in_log(rawLog, "mixed together", Highlander=True, Which="first")
        if len(RLM) != 0:  # if this is not empty
            mix.PreparationDate = RLM.TimeStamp

        # now we can define the mixture
        mix.Synthesis = SynthesisClass(
            ID=f"{solutionId}_Synthesis",
            Name=f"Preparation of {solutionId}",
            Description=" ",
            # SynthesisLog=synth,
            RawLog=rawLog,
        )

        # enter measured density if available
        RLM = find_in_log(rawLog, "density determined", Highlander=True, Which="first")
        if len(RLM) != 0:  # if this is not empty
            mix.Density = RLM.Quantity
        # override density if calculated is present, as measured was done at 20 degrees, and calculated is at lab temp:
        RLM = find_in_log(rawLog, "density calculated", Highlander=True, Which="first")
        if len(RLM) != 0:  # if this is not empty
            mix.Density = RLM.Quantity

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
    StartRLM = find_in_log(
        exp.Synthesis.RawLog,
        "Start injection of solution",
        Highlander=True,
        Which="last",
        # return_indices=True,
    )  # .astimezone('UTC'))#, does this need str-ing?
    ReactionStart = StartRLM.TimeStamp if StartRLM != [] else 0

    StopRLM = find_in_log(
        exp.Synthesis.RawLog,
        "Sample placed in centrifuge",
        Highlander=True,
        Which="last",
        # return_indices=True,
    )  # .astimezone('UTC'))#, does this need str-ing?
    ReactionStop = StopRLM.TimeStamp if StopRLM != [] else 0

    # exp.Synthesis.KeyParameters.update(
    #     {"ReactionTime": ureg.Quantity((ReactionStop - ReactionStart).total_seconds(), "s")}
    # )
    # more detailed logging style also indicating sources and descriptions
    exp.Synthesis.DerivedParameters += [
        DerivedParameter(
            ID="ReactionTime",
            ParameterName="Reaction time",
            Description=(
                "The time between the start of the second injection into the reaction mixture and the start of the"
                " centrifugation"
            ),
            RawMessages=[StartRLM.Index, StopRLM.Index],
            Quantity=ureg.Quantity((ReactionStop - ReactionStart).total_seconds(), "s"),
            Value=(ReactionStop - ReactionStart).total_seconds(),
            Unit="s",
        )
    ]

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

        if "AMSET" in LogEntry.Value:
            sun = LogEntry.Value
        else:
            logging.error("No AMSET configuration found in log, but also not specified as input argument.")
            raise SyntaxError

    # At this point, we need the experimental setup as we need the falcon tube..
    exp.ExperimentalSetup = readExperimentalSetup(filename=logFile, SetupName=sun)

    # now we can create a new mixture
    mix = Mixture(
        ID="ReactionMix_0",
        MixtureName="Reaction Mixture 0",
        Description="The MOF synthesis reaction mixture",
        PreparationDate=ReactionStart,  # idx,  # last timestamp read
        StorageConditions="RT",
        Container=[i for i in exp.ExperimentalSetup.EquipmentList if "falcon tube" in i.EquipmentName.lower()][-1],
    )
    # to this we need to find the volume and density of which solution for the injections
    allVolumes = find_in_log(exp.Synthesis.RawLog, ["Solution", "volume set"], Highlander=False)
    assert len(allVolumes) != 0, "No injection volume specified in log"
    # assert (
    #     len(allVolumes) == 1
    # ), "More than one injection volumes specified in log, dissimilar solution volumes not yet implemented"

    # find calibration factor and offset:
    Syringe = [i for i in exp.ExperimentalSetup.EquipmentList if i.EquipmentName.lower() == "syringe"][-1]
    CalibrationFactor = Syringe.PVs["volume"].CalibrationFactor
    CalibrationOffset = Syringe.PVs["volume"].CalibrationOffset
    allSolutions = find_in_log(exp.Synthesis.RawLog, ["Stop", "injection of solution"], Highlander=False)
    # I don't have the densities yet, so we have to assume something for now
    for solutionRLM in allSolutions:
        solutionId = solutionRLM.Value
        # figure out which volume was used for this by looking at the index:
        for volRLM in allVolumes:
            if volRLM.Index < solutionRLM.Index:
                # the last time we set the volume before injection is the volume used.
                VolumeRLM = volRLM

        # VolumeRLM = allVolumes[0]

        DensityOfAdd = getattr(
            exp.Chemicals.mixtures[solutionId], "Density"
        )  # default does not seem to work, still returns None.
        if DensityOfAdd is None:
            DensityOfAdd = ureg.Quantity("0.792 g/cc")
        print(f"{DensityOfAdd}")
        mix.AddMixture(
            exp.Chemicals.mixtures[solutionId],
            AddMixtureVolume=(
                VolumeRLM.Quantity * CalibrationFactor + CalibrationOffset
            ),  # TODO: correction factor should be added in
            MixtureDensity=DensityOfAdd,
        )
    # Add to the structure.
    exp.Chemicals.mixtures += [mix]

    # calculate the age of solution0 and solution1 into the mix:
    # exp.Synthesis.KeyParameters.update(
    #     {
    #         "MetalSolutionAge": ureg.Quantity(
    #             (
    #                 exp.Chemicals.mixtures[2].PreparationDate - exp.Chemicals.mixtures[0].PreparationDate
    #             ).total_seconds(),
    #             "s",
    #         )
    #     }
    # )
    # more detailed logging style also indicating sources and descriptions
    exp.Synthesis.DerivedParameters += [
        DerivedParameter(
            ID="MetalSolutionAge",
            ParameterName="Metal Solution Age",
            Description=(
                "The time between the preparation of the metal solution and the mixing of the reaction mixture"
            ),
            RawMessages=[],
            Quantity=ureg.Quantity(
                (
                    exp.Chemicals.mixtures[2].PreparationDate - exp.Chemicals.mixtures[0].PreparationDate
                ).total_seconds(),
                "s",
            ),
            Value=(
                exp.Chemicals.mixtures[2].PreparationDate - exp.Chemicals.mixtures[0].PreparationDate
            ).total_seconds(),
            Unit="s",
        )
    ]
    # exp.Synthesis.KeyParameters.update(
    #     {
    #         "LinkerSolutionAge": ureg.Quantity(
    #             (
    #                 exp.Chemicals.mixtures[2].PreparationDate - exp.Chemicals.mixtures[1].PreparationDate
    #             ).total_seconds(),
    #             "s",
    #         )
    #     }
    # )
    # more detailed logging style also indicating sources and descriptions
    exp.Synthesis.DerivedParameters += [
        DerivedParameter(
            ID="LinkerSolutionAge",
            ParameterName="Metal Solution Age",
            Description=(
                "The time between the preparation of the linker solution and the mixing of the reaction mixture"
            ),
            RawMessages=[],
            Quantity=ureg.Quantity(
                (
                    exp.Chemicals.mixtures[2].PreparationDate - exp.Chemicals.mixtures[1].PreparationDate
                ).total_seconds(),
                "s",
            ),
            Value=(
                exp.Chemicals.mixtures[2].PreparationDate - exp.Chemicals.mixtures[1].PreparationDate
            ).total_seconds(),
            Unit="s",
        )
    ]
    # calculate the weight of Product:
    InitialMass = find_in_log(
        exp.Synthesis.RawLog,
        ["empty Falcon tube"],
        excludeString=["+ dry sample", " lid"],
        Highlander=True,
        Which="last",
    )
    FinalMass = find_in_log(
        exp.Synthesis.RawLog, ["of Falcon tube + dry sample"], excludeString=["lid"], Highlander=True, Which="last"
    )

    # WeightRLMs = find_in_log(exp.Synthesis.RawLog, ["Weight", "Falcon"], Highlander=False)
    # targets = ["Weight", "Falcon"]
    # # find me the messages containing both those words:
    # dfMask = df["Readout"].apply(
    #     lambda sentence: all(word in sentence for word in targets)
    # )
    # mLocs = np.where(dfMask)[0]
    logging.debug(f" {InitialMass=}, \n {FinalMass=}")
    # assert len(WeightRLMs) == 2, "more than two weight indications (empty, empty+dry product) were found"
    # exp.Chemicals.final_product.Mass = WeightRLMs[1].Quantity - WeightRLMs[0].Quantity
    exp.Chemicals.final_product.Mass = FinalMass.Quantity - InitialMass.Quantity
    # compute theoretical yield:
    # we need to find out how many moles of metal we have in the previously established reaction mixture
    logging.debug(f"{len(mix.ComponentList)=}")
    methMoles = 0
    for component in mix.ComponentList:
        aNumber = chempy.util.periodic.atomic_number("Zn")
        logging.debug(f"{component.Chemical.Substance.composition.keys()=}")
        if aNumber in component.Chemical.Substance.composition.keys():
            # this is the component we're looking for. How many moles of atoms per moles of substance?
            metalMoles = component.Chemical.Substance.composition[aNumber]
            TotalMetalMoles = mix.ComponentMoles(MatchComponent=component) * metalMoles
        if "C4H6N2" in component.Chemical.Substance.name:
            TotalLinkerMoles = mix.ComponentMoles(MatchComponent=component)
        if "CH3OH" in component.Chemical.Substance.name:
            methMoles += mix.ComponentMoles(MatchComponent=component)
    TotalMethanolMoles = methMoles

    # exp.Synthesis.KeyParameters.update({"MetalToLinkerRatio": TotalLinkerMoles / TotalMetalMoles})
    # more detailed logging style also indicating sources and descriptions
    exp.Synthesis.DerivedParameters += [
        DerivedParameter(
            ID="MetalToLinkerRatio",
            ParameterName="Metal To Linker Ratio",
            Description=(
                "The molar ratio between metal ions and linker molecules, as calculated from the solution"
                " compositions."
            ),
            RawMessages=[],
            Quantity=TotalLinkerMoles / TotalMetalMoles,
            Value=(TotalLinkerMoles / TotalMetalMoles).magnitude,
            Unit=(TotalLinkerMoles / TotalMetalMoles).units,
        )
    ]
    # exp.Synthesis.KeyParameters.update({"MetalToMethanolRatio": TotalMethanolMoles / TotalMetalMoles})
    # more detailed logging style also indicating sources and descriptions
    exp.Synthesis.DerivedParameters += [
        DerivedParameter(
            ID="MetalToMethanolRatio",
            ParameterName="Metal To Methanol Ratio",
            Description=(
                "The molar ratio between metal ions and solvent (methanol) molecules, as calculated from the"
                " solution compositions."
            ),
            RawMessages=[],
            Quantity=TotalMethanolMoles / TotalMetalMoles,
            Value=(TotalMethanolMoles / TotalMetalMoles).magnitude,
            Unit=(TotalMethanolMoles / TotalMetalMoles).units,
        )
    ]

    exp.Chemicals.target_product.Mass = TotalMetalMoles * exp.Chemicals.target_product.Chemical.MolarMass
    logging.debug(f"{exp.Chemicals.SynthesisYield=}")
    exp.Chemicals._storeKeys += ["SynthesisYield"]
    # maybe later
    # exp.Synthesis.ChemicalReaction = chempy.Reaction.from_string("")
    exp.Synthesis.SourceDOI = "TBD"  # TODO: add a default synthesis to Zenodo

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
    # exp.Synthesis.KeyParameters.update({"LabTemperature": LogEntry.Quantity})
    exp.Synthesis.DerivedParameters += [
        DerivedParameter(
            ID="LabTemperature",
            ParameterName="Laboratory temperature",
            Description="The temperature of the laboratory as measured about 0.5m above the reaction falcon tubes",
            RawMessages=[LogEntry.Index],
            Quantity=LogEntry.Quantity,
            Value=LogEntry.Value,
            Unit=LogEntry.Unit,
        )
    ]
    # injection speed:
    LogEntry = find_in_log(
        exp.Synthesis.RawLog,
        ["Solution", "rate set"],
        Highlander=True,
        Which="last",
        # return_indices=True,
    )
    # exp.Synthesis.KeyParameters.update({"InjectionSpeed": LogEntry.Quantity})
    exp.Synthesis.DerivedParameters += [
        DerivedParameter(
            ID="InjectionSpeed",
            ParameterName="Injection Speed",
            Description="The speed at which the second reactant was added to the reaction mixture",
            RawMessages=[LogEntry.Index],
            Quantity=LogEntry.Quantity,
            Value=LogEntry.Value,
            Unit=LogEntry.Unit,
        )
    ]
    # exp.Synthesis.KeyParameters.update({"SynthesisYield": exp.Chemicals.SynthesisYield})
    exp.Synthesis.DerivedParameters += [
        DerivedParameter(
            ID="SynthesisYield",
            ParameterName="Synthesis Yield",
            Description="The yield of the synthesis as calculated from the final product mass",
            RawMessages=[InitialMass.Index, FinalMass.Index],
            Quantity=exp.Chemicals.SynthesisYield,
            Value=exp.Chemicals.SynthesisYield.magnitude,
            Unit=exp.Chemicals.SynthesisYield.units,
        )
    ]
    # add notes to the KeyParameters:
    noteCounter = 0
    noteList = find_in_log(
        exp.Synthesis.RawLog,
        "Note",
        Highlander=False,
        # Which="last",
        # return_indices=True,
    )
    for note in noteList:
        # exp.Synthesis.KeyParameters.update({f"Note{noteCounter}": note.Value})
        exp.Synthesis.DerivedParameters += [
            DerivedParameter(
                ID="Note{noteCounter}",
                ParameterName="Note {noteCounter}",
                Description="An operator note or flag as pertaining to the synthesis",
                RawMessages=[note.Index],
                Quantity=note.Quantity,
                Value=note.Value,
                Unit=note.Unit,
            )
        ]
    # print([i.Value for i in noteList])

    # lastly, we can remove all the unused reagents from starting_compounds:
    exp.Chemicals.starting_compounds = [item for item in exp.Chemicals.starting_compounds if item.Used]

    return exp
