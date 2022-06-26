import typer
from kubecfg.config import KubeConfig
from typing import Optional
import httpx
from rich import print_json
from rich import print as rich_print
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
    if "metadata" in root_symbol.keys():
        symbol_copy["_m"] = root_symbol["metadata"]  # Create a data loopback
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
        reply = http_client.get(url)
    except httpx.ConnectTimeout:
        rich_print(
            "[red]Timeout while trying to get answer from server[/]", file=sys.stderr
        )
        exit(2)
    reply.raise_for_status()
    return reply.json()


def get(
    endpoint_path: Optional[str] = typer.Argument(
        "", help="Path within the API endpoint"
    ),
    format: Optional[str] = typer.Option("", "-f", help="Path within the API endpoint"),
    timeout: Optional[int] = 30,
    insecure: bool = typer.Option(
        False, "--insecure", "-k", help="Ignore SSL validation errors"
    ),
    json: bool = typer.Option(False, "--json", "-j", help="Force output to JSON"),
    pretty: bool = typer.Option(
        False, "--pretty", "-p", help="Pretty print the result"
    ),
):
    """ Perform get into server """
    if pretty:
        my_print = rich_print
    else:
        my_print = print

    kubeconfig = KubeConfig()
    kubeconfig.load_config()
    context_name = kubeconfig.current_context
    if context_name is None:
        my_print(
            "[red]You have no current context, please provide a context name[/]",
            file=sys.stderr,
        )
        exit(1)
    try:
        auth_data = kubeconfig.get_auth_data(context_name)
    except KeyError:
        rich_print(
            f"Context '[bold red]{context_name}[/]' was not found!", file=sys.stderr
        )
        available_contexts = ", ".join([k.name for k in kubeconfig.contexts])
        rich_print(
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
                if json:
                    print_json(data=template.render(x))
                else:
                    my_print(template.render(x))
            exit(0)
        reply_data = Template(format).render(reply_data)
    else:
        json = True
    if json:
        print_json(data=reply_data)
    else:
        my_print(reply_data)
