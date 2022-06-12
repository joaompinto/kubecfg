state = {"verbose": False}


def main(verbose: bool = False):
    """
    Utility to show and test kubernetes client configurations
    """
    if verbose:
        state["verbose"] = True
