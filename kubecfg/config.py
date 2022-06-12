import os
import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table

KUBE_CONFIG_DEFAULT_LOCATION = os.environ.get("KUBECONFIG", "~/.kube/config")


class ConfigException(Exception):
    pass


class KubeConfig:
    def __init__(self):
        self.path = Path(KUBE_CONFIG_DEFAULT_LOCATION).expanduser()
        self.console = Console()

    def load_config(self):

        path = self.path
        if not path.exists():
            raise ConfigException(
                "Kube config file not found at " "%s file is empty" % self.path
            )

        with open(path) as f:
            config = yaml.safe_load(f)

        if config is None:
            raise ConfigException(
                "Invalid kube-config. " "%s file is empty" % self.path
            )
        self.config = config
        return config

    def show_clusters(self):

        table = Table(title="Clusters")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Server")

        clusters = self.config.get("clusters")
        if clusters is None:
            raise ConfigException(
                "Invalid kube-config. " "%s has no clusters defined" % self.path
            )
        for cluster in clusters:
            table.add_row(cluster["name"], cluster["cluster"]["server"])
        self.console.print(table)

    def show_contexts(self):
        table = Table(title="Contexts")
        table.add_column("Name", style="cyan")
        table.add_column("Cluster")
        table.add_column("Namespace")
        table.add_column("User")

        contexts = self.config.get("contexts")
        if contexts is None:
            raise ConfigException(
                "Invalid kube-config. " "%s has no contexts defined" % self.path
            )
        for context in contexts:
            cluster = context["context"].get("cluster")
            namespace = context["context"].get("namespace")
            user = context["context"].get("user")
            table.add_row(context["name"], cluster, namespace, user)
        self.console.print(table)

    def show_users(self):
        table = Table(title="Users")
        table.add_column("Name", style="cyan")
        table.add_column("Cert")
        table.add_column("Key")

        users = self.config.get("users")
        if users is None:
            raise ConfigException(
                "Invalid kube-config. " "%s has no users defined" % self.path
            )
        for user in users:
            cert = user["user"].get("client-certificate", " -- data --")
            key = user["user"].get("client-key", " -- data -- ")
            cert = cert.replace(str(Path.home()), "~")
            key = key.replace(str(Path.home()), "~")
            table.add_row(user["name"], cert, key)
        self.console.print(table)

    def show_current(self):
        current = self.config.get("current-context")
        if current:
            self.console.print(f"Current Context: [bold green]{current}[/]")
