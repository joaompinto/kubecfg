import typer
from kubecfg.config import KubeConfig
from typing import Optional
import httpx
from rich import print_json
import sys
from dinterpol import Template
import copy


def exended_symbol(symbol, root_symbol=None):
    if not isinstance(symbol, dict):
        return symbol
    if root_symbol is None:
        root_symbol = symbol
    symbol_copy = copy.copy(symbol)
    symbol_copy["_"] = root_symbol  # Create a data loopback
    metadata = root_symbol.get("metadata")
    if metadata:
        symbol_copy["_m"] = metadata  # Create a data loopback
        symbol_copy["_n"] = metadata.get("name", "-")  # Create a data loopback
        symbol_copy["_l"] = metadata.get("labels", {})
        symbol_copy["_a"] = metadata.get("annotations", {})
    if "status" in root_symbol.keys():
        symbol_copy["_s"] = root_symbol.get("status", "-")  # Create a data loopback
    return symbol_copy


def httpx_client_get(auth_data, endpoint_path, timeout, insecure):
    if len(auth_data) == 3:
        server, cert, client_ca = auth_data
        if insecure:
            client_ca = False
        http_client = httpx.Client(cert=cert, verify=client_ca, timeout=timeout)
    else:
        server, token = auth_data
        http_client = httpx.Client(
            headers={"Authorization": f"Bearer {token}"},
            timeout=timeout,
            verify=not insecure,
        )

    url = f"{server}/{endpoint_path}"
    try:
        response = http_client.get(url)
    except httpx.ConnectTimeout:
        print("[red]Timeout while trying to get answer from server[/]", file=sys.stderr)
        exit(2)
    response.raise_for_status()
    return response.json()


def get(
    endpoint_path: Optional[str] = typer.Argument(
        "", help="Path within the API endpoint"
    ),
    simple_format: Optional[str] = typer.Argument(None, help="Simple format string"),
    format: Optional[str] = typer.Option("", "-f", help="f-string for the output"),
    timeout: Optional[int] = 30,
    insecure: bool = typer.Option(
        False, "--insecure", "-k", help="Ignore SSL validation errors"
    ),
    watch: bool = typer.Option(
        False, "--watch", "-w", help="Watch resource for changes"
    ),
    pretty: bool = typer.Option(
        False, "--pretty", "-p", help="Pretty print the result"
    ),
):
    """Perform get into server"""

    kubeconfig = KubeConfig()
    kubeconfig.load_config()

    if simple_format:
        new_format = ""
        tokens = simple_format.split(" ")
        new_format = " ".join([f"{{{token}}}" for token in tokens])
        format = new_format

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

    reply_data = httpx_client_get(auth_data, endpoint_path, timeout, insecure)
    if format:
        reply_data = exended_symbol(reply_data)
        if "items" in reply_data.keys():
            template = Template(format)
            for item in reply_data["items"]:
                x = exended_symbol(item["metadata"], item)
                data = template.render(x)
                if isinstance(data, dict):
                    print_json(data=data)
                else:
                    print(data)
            exit(0)
        reply_data = Template(format).render(reply_data)

    if isinstance(reply_data, dict):
        print_json(data=reply_data)
    else:
        print(reply_data)
