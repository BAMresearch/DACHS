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
from dachs.synthesis import DerivedParameter, RawLogMessage, SynthesisClass, synthesisStep


def DParFromLogEntry(ID: str, ParameterName: str, Description: str, LogEntry: RawLogMessage):
    return DerivedParameter(
        ID=ID,
        ParameterName=ParameterName,
        Description=Description,
        RawMessages=[LogEntry.Index],
        Quantity=LogEntry.Quantity,
        Value=LogEntry.Value,
        Unit=LogEntry.Unit,
    )


def create(logFile: Path, solFiles: List[Path], synFile: Path, amset: str = None) -> Experiment:
    """
    Construction of a test structure from Glen's excel files using the available dataclasses,
    the hope is to use this as a template to construct the ontology, then write the structure to HDF5 files.

    It now defines:
        - base Chemicals and
        - Mixtures

    **TODO**:
        - write synthesis log
        - write or (perhaps better) link to SAS data structure.
        - write or (perhaps better) link to analysis results?

    :param logFile: Path to the robot log book Excel file
    :param solFiles: One or more Excel files describing the base solutions which were mixed by the robot
    :param synFile: The synthesis robot log file.
    """
    logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
    # logging to files not working yet. Do I have to 'emit' and close?
    # logger = logging.getLogger()
    # fh = logging.FileHandler(Path(synFile.parent, synFile.stem + "DachsifyWarnings.log"), mode="w")
    # fh.setLevel(logging.WARNING)
    # fh2 = logging.FileHandler(Path(synFile.parent, synFile.stem + "DachsifyInfo.log"), mode="w")
    # fh2.setLevel(logging.INFO)
    # logger.addHandler(fh)
    # logger.addHandler(fh2)
    logging.info(f"Working in '{os.getcwd()}'.")

    # define a ZIF 8 Chemical, we'll need this later:
    z8 = chempy.Substance.from_formula("C8H10N4Zn")
    zifChemical = Chemical(
        ChemicalID="ZIF-8",
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
        ChemicalID="ZIF-L",
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
        ExperimentName="Automatic MOF Exploration series",
        Description="""
            In this series, MOFs are synthesised in methanol from two stock solutions,
            all performed at room temperature (see environmental details in log).
            The injection rate and injection order are varied. Centrifugation and drying
            is performed manually. Residence times are ca. 20 minutes after start of second injection.
        """,
        # in this experiment, we are going to use some chemicals. These are defined by the chemicals class.
        Chemicals=ChemicalsClass(
            # There is a list of starting compounds in the log file
            StartingCompounds=ReadStartingCompounds(logFile),
            Mixtures=[],  # Mixtures get filled in later
            # Then we have the potential products from the synthesis. Be as thorough as you like here, it will help you later on
            PotentialProducts=[
                Product(ID="ZIF-8", Chemical=zifChemical),
                Product(ID="ZIF-L", Chemical=zifLChemical),
            ],
            # the target product is what you are aiming to get:
            TargetProduct=Product(ID="TargetProduct", Chemical=zifChemical),
            # the final product is what you actually got in the end, as evidenced by the evidence.
            FinalProduct=Product(
                ID="FinalProduct", Chemical=zifChemical, Evidence="Assumed for now ¯\_(ツ)_/¯"
            ),  # mass is set later.
        ),
    )

    logging.info("defining the Mixtures based on Mixtures of starting compounds")

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
            PreparationDate=pd.to_datetime(0, utc=True),  # idx,  # will be replaced with last timestamp read
            StorageConditions="RT",
        )

        # new style 20230919, attempting to get rid of synthesisStep
        aNumber = chempy.util.periodic.atomic_number("Zn")
        mixIsMetal = False
        mixIsLinker = False
        # see known issue on the BAMResearch DACHS Git.. this is to avoid false matches when using overlapping names:
        ReagentIDsUsedInSynthesis = [i.Value for i in find_in_log(rawLog, "ReagentID", Highlander=False)]
        # print(f"{ReagentIDsUsedInSynthesis=}")
        for reagent in exp.Chemicals.StartingCompounds:
            RLMList = find_in_log(rawLog, [reagent.ID, "mass of"], Highlander=False, raiseWarning=False)
            if RLMList is not None:  # if the list is not empty:
                for RLM in RLMList:  # add each to the mix
                    # find the preceding message to ensure the reagentID is correct:
                    previousRLM = [i for i in rawLog if i.Index == (RLM.Index - 1)][-1]
                    logging.info(f"{reagent.ID=}, {previousRLM.Value=}, so: {reagent.ID==previousRLM.Value}")
                    if reagent.ID in ReagentIDsUsedInSynthesis:
                        # no idea why I can't also check for this match: reagent.ID==previousRLM.Value, I get a problem later on
                        mix.add_reagent_to_mix(reag=reagent, ReagentMass=RLM.Quantity)
                        if aNumber in reagent.Chemical.Substance.composition.keys():
                            mixIsMetal = True
                        if "C4H6N2" in reagent.Chemical.Substance.name:
                            mixIsLinker = True

        if mixIsMetal:
            mix.Description = "Metal salt dispersion"
        if mixIsLinker:
            mix.Description = "Organic linker dispersion"

        RLM = find_in_log(rawLog, "mixed together", Highlander=True, Which="first")
        if RLM is not None:  # if this is not empty
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
        RLM = find_in_log(rawLog, "density determined", Highlander=True, Which="first", raiseWarning=False)
        if RLM is not None:  # if this is not empty
            mix.Density = RLM.Quantity
        # override density if calculated is present, as measured was done at 20 degrees, and calculated is at lab temp:
        RLM = find_in_log(rawLog, "density calculated", Highlander=True, Which="first", raiseWarning=False)
        if RLM is not None:  # if this is not empty
            mix.Density = RLM.Quantity
        # fix the detailed description, clipping off the last ', and ':
        mix.DetailedDescription = mix.DetailedDescription[:-6]
        exp.Chemicals.Mixtures += [mix]

    logging.info("defining the synthesis log")

    exp.Synthesis = SynthesisClass(
        ID="Synthesis",
        Name="MOF standard synthesis in MeOH, room temperature, nominally 20 minute residence time",
        # description gets added at the end with actual values...
        RawLog=readRawMessageLog(synFile),
    )

    # After our discussion, we've decided not to focus on including derived parameters just yet.
    # We still need a few things though.
    logging.info("Extracting the derived parameters")
    # minimal derived information:
    # add the reaction Mixtures to Chemicals.Mixtures
    # for the start time we need the last "start injection of solution" timestamp
    StartRLM = find_in_log(
        exp.Synthesis.RawLog,
        "Start injection of solution",
        Highlander=True,
        Which="last",
        # return_indices=True,
    )  # .astimezone('UTC'))#, does this need str-ing?
    ReactionStart = StartRLM.TimeStamp if StartRLM is not None else pd.to_datetime(0, utc=True)

    StopRLM = find_in_log(
        exp.Synthesis.RawLog,
        "Sample placed in centrifuge",
        Highlander=True,
        Which="first",
        # return_indices=True,
    )  # .astimezone('UTC'))#, does this need str-ing?
    ReactionStop = StopRLM.TimeStamp if StopRLM is not None else pd.to_datetime(0, utc=True)

    # more detailed logging style also indicating sources and descriptions
    if StartRLM is not None and StopRLM is not None:
        exp.Synthesis.DerivedParameters += [
            DerivedParameter(
                ID="ReactionTime",
                ParameterName="Reaction time",
                Description=(
                    "The time between the start of the second injection into the reaction mixture and the start of"
                    " the centrifugation"
                ),
                RawMessages=[StartRLM.Index, StopRLM.Index],
                Value=(ReactionStop - ReactionStart).total_seconds(),
                Unit="s",
            )
        ]
    # if values are not there, I'm no longer making dummy entries as per Ingo's suggestion. keeps the code clean.

    if amset is not None:
        sun = amset

    # override with info in log if present:
    LogEntry = find_in_log(
        exp.Synthesis.RawLog,
        "SetupID",
        Highlander=True,
        Which="last",
        # return_indices=True,
    )
    if LogEntry is not None:
        if "AMSET" in LogEntry.Value:
            sun = LogEntry.Value  # override if in the log
    if (LogEntry is None) & (amset is None):
        logging.error("No AMSET configuration found in log, but also not specified as input argument.")
        raise SyntaxError
    logging.info(f"SetupName: {sun}")
    # At this point, we need the experimental setup as we need the falcon tube..
    exp.ExperimentalSetup = readExperimentalSetup(filename=logFile, SetupName=sun)
    # print(exp.ExperimentalSetup)
    # now we can create a new mixture
    mix = Mixture(
        ID="ReactionMix0",
        MixtureName="Reaction Mixture 0",
        Description="The MOF synthesis reaction mixture",
        PreparationDate=ReactionStart,  # idx,  # last timestamp read
        StorageConditions="RT",
        Container=[i for i in exp.ExperimentalSetup.EquipmentList if "falcon tube" in i.EquipmentName.lower()][-1],
    )
    # to this we need to find the volume and density of which solution for the injections
    # TODO: do something better to separate solution numbers and their respective volumes.
    allVolumes = find_in_log(exp.Synthesis.RawLog, ["Solution", "volume set"], Highlander=False)
    if allVolumes is None:
        logging.error(f"No injection volume specified in {synFile.stem}")

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
                # the last time we set the volume before injection is the volume used. WROMG, WROMG, WROMG, WROMG, WROMG, WROMG, WROMG, WROMG, WROMG, WROMG! see, A4_T006 TODO: fix
                VolumeRLM = volRLM

        # VolumeRLM = allVolumes[0]

        DensityOfAdd = getattr(
            exp.Chemicals.Mixtures[solutionId], "Density"
        )  # default does not seem to work, still returns None.
        if DensityOfAdd is None:
            DensityOfAdd = ureg.Quantity("0.792 g/cc")
        # print(f"{DensityOfAdd=}")
        mix.add_mixture_to_mix(
            exp.Chemicals.Mixtures[solutionId],
            AddMixtureVolume=(
                VolumeRLM.Quantity * CalibrationFactor + CalibrationOffset
            ),  # TODO: correction factor should be added in
            MixtureDensity=DensityOfAdd,
        )
    # clip off the last auto-generated ', and ' from the detailed description
    mix.DetailedDescription = mix.DetailedDescription[:-6]
    # Add to the structure.
    exp.Chemicals.Mixtures += [mix]

    # calculate the age of solution0 and solution1 into the mix:
    exp.Synthesis.DerivedParameters += [
        DerivedParameter(
            ID="MetalSolutionAge",
            ParameterName="Metal Solution Age",
            Description=(
                "The time between the preparation of the metal solution and the mixing of the reaction mixture"
            ),
            RawMessages=[],
            Value=(
                exp.Chemicals.Mixtures[2].PreparationDate - exp.Chemicals.Mixtures[0].PreparationDate
            ).total_seconds(),
            Unit="s",
        )
    ]

    # age of the linker solution
    exp.Synthesis.DerivedParameters += [
        DerivedParameter(
            ID="LinkerSolutionAge",
            ParameterName="Metal Solution Age",
            Description=(
                "The time between the preparation of the linker solution and the mixing of the reaction mixture"
            ),
            RawMessages=[],
            Value=(
                exp.Chemicals.Mixtures[2].PreparationDate - exp.Chemicals.Mixtures[1].PreparationDate
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

    # mLocs = np.where(dfMask)[0]
    logging.debug(f" {InitialMass=}, \n {FinalMass=}")
    exp.Chemicals.FinalProduct.Mass = FinalMass.Quantity - InitialMass.Quantity
    # compute theoretical yield:
    # we need to find out how many moles of metal we have in the previously established reaction mixture
    logging.debug(f"{len(mix.ComponentList)=}")
    metMoles = 0
    methMoles = 0
    linkMoles = 0
    aNumber = chempy.util.periodic.atomic_number("Zn")
    for component in mix.ComponentList:
        logging.debug(f"{component.Chemical.Substance.composition.keys()=}")
        if aNumber in component.Chemical.Substance.composition.keys():
            # this is the component we're looking for. How many moles of atoms per moles of substance?
            metalMoles = component.Chemical.Substance.composition[
                aNumber
            ]  # just in case we have more metal ions per mole of chem.
            metMoles += mix.component_moles(MatchComponent=component) * metalMoles
        if "C4H6N2" in component.Chemical.Substance.name:
            linkMoles += mix.component_moles(MatchComponent=component)
        if "CH3OH" in component.Chemical.Substance.name:
            methMoles += mix.component_moles(MatchComponent=component)
    TotalMetalMoles = metMoles
    TotalLinkerMoles = linkMoles
    TotalMethanolMoles = methMoles

    logging.info(f"{TotalMetalMoles=}, {TotalLinkerMoles=}, {TotalMethanolMoles=}")

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
            Value=(TotalMethanolMoles / TotalMetalMoles).magnitude,
            Unit=(TotalMethanolMoles / TotalMetalMoles).units,
        )
    ]

    # The yield is calculated from the target mass versus the actual product mass.
    exp.Chemicals.TargetProduct.Mass = TotalMetalMoles * exp.Chemicals.TargetProduct.Chemical.MolarMass
    logging.debug(f"{exp.Chemicals.SynthesisYield=}")
    exp.Chemicals._storeKeys += ["SynthesisYield"]
    # maybe later
    # exp.Synthesis.SourceDOI = "TBD"  # TODO: add a default synthesis to Zenodo

    # We calculate an extra theoretical yield based on the moles of linker:
    LinkerBasedProductMass = TotalLinkerMoles / 2 * exp.Chemicals.TargetProduct.Chemical.MolarMass
    exp.Synthesis.DerivedParameters += [
        DerivedParameter(
            ID="SynthesisYieldLinker",
            ParameterName="Linker-based synthesis yield",
            Description="The synthesis yield as calculated based on full conversion of the available linker.",
            RawMessages=[],
            Value=(exp.Chemicals.FinalProduct.Mass / LinkerBasedProductMass).magnitude,
            Unit=(exp.Chemicals.FinalProduct.Mass / LinkerBasedProductMass).units,
        )
    ]

    # store the room temperature:
    LogEntry = find_in_log(
        exp.Synthesis.RawLog,
        "Environmental temperature",
        Highlander=True,
        Which="last",
        # return_indices=True,
    )
    # exp.Synthesis.KeyParameters.update({"LabTemperature": LogEntry.Quantity})
    if LogEntry is not None:
        exp.Synthesis.DerivedParameters += [
            DParFromLogEntry(
                "LabTemperature",
                "Laboratory temperature",
                "The temperature of the laboratory as measured about 0.5m above the reaction falcon tubes",
                LogEntry,
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
    if LogEntry is not None:
        exp.Synthesis.DerivedParameters += [
            DParFromLogEntry(
                "InjectionSpeed",
                "Injection Speed",
                "The speed at which the second reactant was added to the reaction mixture",
                LogEntry,
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
    if noteList is not None:
        for note in noteList:
            exp.Synthesis.DerivedParameters += [
                DParFromLogEntry(
                    f"Note{noteCounter}",
                    f"Note {noteCounter}",
                    "An operator note or flag as pertaining to the synthesis",
                    note,
                )
            ]

    # lastly, we can prune all the unused reagents from StartingCompounds:
    exp.Chemicals.StartingCompounds = [item for item in exp.Chemicals.StartingCompounds if item.Used]

    # Finally, we add the text description:
    # TODO: specify the order and delay between the solution injections
    # TODO: stirring speed RPM

    CentrifugeSpeed = find_in_log(
        exp.Synthesis.RawLog,
        ["Sample", "placed in centrifuge"],
        Highlander=True,
        Which="last",
    )
    if LogEntry is not None:
        exp.Synthesis.DerivedParameters += [
            DParFromLogEntry("CentrifugeSpeed", "Centrifuge Speed", "The speed of centrifugation", CentrifugeSpeed)
        ]
    CentrifugeDuration = find_in_log(
        exp.Synthesis.RawLog,
        ["Centrifuge", "set time"],
        Highlander=True,
        Which="last",
    )
    if LogEntry is not None:
        exp.Synthesis.DerivedParameters += [
            DParFromLogEntry(
                "CentrifugeDuration", "Centrifuge Duration", "The duration of centrifugation", CentrifugeDuration
            )
        ]
    OvenStop = find_in_log(
        exp.Synthesis.RawLog,
        ["Sample", "removed from oven"],
        Highlander=True,
        Which="last",
    )
    OvenStart = find_in_log(
        exp.Synthesis.RawLog,
        ["Sample", "oven"],
        Highlander=True,
        Which="first",
    )
    if LogEntry is not None:
        exp.Synthesis.DerivedParameters += [
            DParFromLogEntry(
                "OvenTemperature", "Oven Temperature", "The setpoint temperature of the drying oven", OvenStart
            )
        ]
    if OvenStart is not None and OvenStop is not None:
        exp.Synthesis.DerivedParameters += [
            DerivedParameter(
                ID="ForcedDryingDuration",
                ParameterName="Forced Drying Duration",
                Description=(
                    "The duration of the oven drying, i.e. between placing the sample in the oven and taking it"
                    " out again"
                ),
                RawMessages=[OvenStart.Index, OvenStop.Index],
                Value=(OvenStop.TimeStamp - OvenStart.TimeStamp).total_seconds(),
                Unit="s",
            )
        ]
    StirrerBar = [i for i in exp.ExperimentalSetup.EquipmentList if ("Stirrer Bar" in i.EquipmentName)][0]
    if StirrerBar is not None:
        exp.Synthesis.DerivedParameters += [
            DerivedParameter(
                ID="StirrerBarModel",
                ParameterName="Stirrer Bar Model",
                Description=(
                    f"The stirrer bar is from {StirrerBar.Manufacturer}, model: {StirrerBar.ModelName}, model"
                    f" number {StirrerBar.ModelNumber}."
                ),
                RawMessages=[StirrerBar.ID],
                Value=StirrerBar.ModelName,
            )
        ]

    # Injection orders, we'll just read this from the SampleID letter...
    SIDLetter = exp.Synthesis.RawLog[0].SampleID[0]
    assert SIDLetter in ["T", "L", "M", "H", "P"]
    if SIDLetter == "T":
        OrderDescription = "The two solutions were added simultaneously."
    elif SIDLetter == "L":
        OrderDescription = (
            "The linker solution was added in a pre-injection step, after which the metal solution was added at"
            " the specified injection rate."
        )
    elif SIDLetter == "M":
        OrderDescription = (
            "The metal solution was added in a pre-injection step, after which the linker solution was added at"
            " the specified injection rate."
        )
    elif SIDLetter == "H":
        OrderDescription = (
            "The metal solution was added in a pre-injection step, after which the linker solution was added"
            " through a hand pour as fast as possible. Both solutions were prepared using the syringe injector."
        )
    elif SIDLetter == "P":
        OrderDescription = (
            "The metal solution was added in a pre-injection step, after which the linker solution was added"
            " through a hand pour as fast as possible. Both solutions were prepared using a pipette."
        )
    else:
        OrderDescription = ""

    # defaults for text generation:
    DPars = {
        "ReactionTime": ureg.Quantity(-1.0, "s"),
        "MetalSolutionAge": ureg.Quantity(-1.0, "s"),
        "LinkerSolutionAge": ureg.Quantity(-1.0, "s"),
        "MetalToLinkerRatio": ureg.Quantity(-1.0, "dimensionless"),
        "MetalToMethanolRatio": ureg.Quantity(-1.0, "dimensionless"),
        "SynthesisYieldLinker": ureg.Quantity(-1.0, "dimensionless"),
        "LabTemperature": ureg.Quantity(-1.0, "degC"),
        "InjectionSpeed": ureg.Quantity(-1.0, "ml/min"),
        "SynthesisYield": ureg.Quantity(-1.0, "dimensionless"),
        "CentrifugeSpeed": ureg.Quantity(-1.0, "rpm"),
        "CentrifugeTime": ureg.Quantity(-1.0, "s"),
        "OvenTemperature": ureg.Quantity(-1.0, "degC"),
        "ForcedDryingDuration": ureg.Quantity(-1.0, "s"),
        "StirrerBarModel": "Unknown",
        "OrderDescription": "Unknown injection order",
    }
    [DPars.update({i.ID: i}) for i in exp.Synthesis.DerivedParameters if isinstance(i, DerivedParameter)]
    Mixes = [i for i in exp.Chemicals.Mixtures if isinstance(i, Mixture)]
    ReactionMix = [i for i in Mixes if i.ID == "ReactionMix0"][0]
    S0Mix = [i for i in Mixes if i.ID == "Solution0"][0]
    S1Mix = [i for i in Mixes if i.ID == "Solution1"][0]
    addKeys = ["OrderDescription", "S0Mix", "S1Mix", "ReactionMix", "OvenStop"]

    for key in addKeys:
        if key in locals():
            DPars[key] = locals()[key]
        else:
            logging.warning(f"{key=} not found in locals, cannot be added to DPars.")
    for key in DPars:
        if DPars[key] == []:  # empty list issue
            logging.warning(f"{key=} in DPars is an empty list, probably missing from {synFile.stem}")
    # print(DPars.keys())
    # we read the template text per automof, and then format it using the information in DPars.
    descText = ""
    try:
        descText = (Path(synFile.parent) / "SynthesisTemplate.txt").read_text().format(**DPars)
    except Exception as e:
        logging.warning("Issue encountered when rendering text from template:")
        logging.exception(e)

    # add notes if they exist to the end of the synthesis text.
    if len(noteList) > 0:
        for Notei, Note in enumerate(noteList):
            descText += f"Note {Notei}: {Note.Value}"

    exp.Synthesis.Description = descText

    return exp
