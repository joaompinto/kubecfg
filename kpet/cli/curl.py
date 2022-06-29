import sys
from typing import Optional

import typer
from rich import print

from kpet.config import KubeConfig


def curl(
    context_name: Optional[str] = typer.Argument(None, help="The name of the image"),
    timeout: Optional[int] = 30,
    insecure: bool = typer.Option(False, "--insecure", "-k"),
):
    """Provide curl command to interact with the API server"""
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
        auth_data = kubeconfig.get_auth_data(context_name)
    except KeyError:
        print(f"Context '[bold red]{context_name}[/]' was not found!", file=sys.stderr)
        available_contexts = ", ".join([k.name for k in kubeconfig.contexts])
        print(
            f"Available contexts: [bold cyan]{available_contexts}[/]", file=sys.stderr
        )
        exit(1)
    if len(auth_data) == 3:
        server, cert, client_ca = auth_data
        if insecure or not client_ca:
            client_ca_str = "-k"
        else:
            client_ca_str = f'--cacert "{client_ca}"'
        client_cert_file, client_key_file = cert
        curl_msg = f'curl {client_ca_str} --cert "{client_cert_file}" --key "{client_key_file}" {server}/'
    else:
        server, token = auth_data
        curl_msg = f'curl -H "Authorization: Bearer {token}" {server}/'
    print(curl_msg)
