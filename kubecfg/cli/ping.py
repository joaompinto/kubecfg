import typer
from kubecfg.config import KubeConfig
from typing import Optional
import httpx
from rich import print
import sys


def ping(
    context_name: Optional[str] = typer.Argument(None, help="The name of the image"),
    timeout: Optional[int] = 30,
):
    """ check if the API server is available """
    kubeconfig = KubeConfig()
    kubeconfig.load_config()
    if context_name is None:
        context_name = kubeconfig.current_context
    if context_name is None:
        print(
            "[red]You have no current context, please provide a context name[/]",
            file=sys.stderr,
        )
        exit(1)
    try:
        server, cert, client_ca = kubeconfig.get_auth_data(context_name)
    except KeyError:
        print(f"Context '[bold red]{context_name}[/]' was not found!", file=sys.stderr)
        available_contexts = ", ".join([k.name for k in kubeconfig.contexts])
        print(
            f"Available contexts: [bold cyan]{available_contexts}[/]", file=sys.stderr
        )
        exit(1)

    http_client = httpx.Client(cert=cert, verify=client_ca, timeout=timeout)
    print(f"Pinging {context_name} at {server} ... ", end="")
    try:
        r = http_client.get(server)
    except httpx.ConnectTimeout:
        print("[red]Timeout while trying to get answer from server[/]", file=sys.stderr)
        exit(2)
    r.raise_for_status()
    print(r)

    version_url = f"{server}/version"
    r = http_client.get(version_url)
    r.raise_for_status()
    print(r.text)
