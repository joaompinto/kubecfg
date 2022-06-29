import typer
from metadict import MetaDict

state = MetaDict({"verbose": False})


def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Ignore SSL validation errors"
    )
):
    """
    Utility to show and test kubernetes client configurations
    """
    if verbose:
        state["verbose"] = True
