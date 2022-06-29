import typer

from kpet.config import KubeConfig


def show(
    all: bool = typer.Option(False, "--all", "-a", help="Show all config"),
):
    """show the kubeconfig [add -a to show all]"""
    kubeconfig = KubeConfig()
    kubeconfig.load_config()
    if all:
        kubeconfig.show_clusters()
        kubeconfig.show_contexts()
        kubeconfig.show_users()
        kubeconfig.show_current()
    else:
        kubeconfig.show_current(name_only=False)
