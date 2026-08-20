"""Part 1 discovery pipeline. Each phase is a package; later phases are scaffolded until implemented."""

PHASE_PACKAGES = {
    0: "src.qualify",
    1: "src.ingest",
    2: "src.process",
    3: "src.analyze",
    4: "src.synthesize",
    5: "src.score",
    6: "src.dashboard",
    7: "src.ideate",
}

PHASE_COMMANDS = {
    0: "python -m src.qualify",
    1: "python -m src.ingest.build",
    2: "python -m src.process",
    3: "python -m src.analyze",
    4: "python -m src.synthesize",
    5: "python -m src.score",
    6: "python -m src.dashboard",
    7: "python -m src.ideate",
}
