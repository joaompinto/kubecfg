from base64 import b64decode
import os
from tempfile import NamedTemporaryFile
import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table
from metadict import MetaDict


KUBE_CONFIG_DEFAULT_LOCATION = os.environ.get("KUBECONFIG", "~/.kube/config")


class ConfigException(Exception):
    pass


class KubeConfig:
    def __init__(self):
        self.path = Path(KUBE_CONFIG_DEFAULT_LOCATION).expanduser()
        self.console = Console()
        self.config = None

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
        self.config = MetaDict(config)
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
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Cluster")
        table.add_column("Namespace")
        table.add_column("User")

        contexts = self.config.get("contexts")
        if contexts is None:
            raise ConfigException(
                "Invalid kube-config. " "%s has no contexts defined" % self.path
            )
        for context in contexts:
            cluster = context.context.get("cluster")
            namespace = context.context.get("namespace")
            user = context.context.get("user")
            table.add_row(context["name"], cluster, namespace, user)
        self.console.print(table)

    def show_users(self):
        table = Table(title="Users")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Cert")
        table.add_column("Key")

        users = self.config.get("users")
        if users is None:
            raise ConfigException(
                "Invalid kube-config. " "%s has no users defined" % self.path
            )
        for user in users:
            cert = user["user"].get("client-certificate", "-- data --")
            key = user["user"].get("client-key", "-- data --")
            if user.user.get("token"):
                cert = "-- token --"
                key = "-- token --"
            cert = cert.replace(str(Path.home()), "~")
            key = key.replace(str(Path.home()), "~")
            table.add_row(user["name"], cert, key)
        self.console.print(table)

    def show_current(self):
        current = self.config.get("current-context")
        if current:
            self.console.print(
                f"Current Context: [bold green]{self.current_context}[/]"
            )

    @property
    def contexts(self):
        return self.config.contexts

    @property
    def clusters(self):
        return self.config.clusters

    @property
    def users(self):
        return self.config.users

    @property
    def current_context(self):
        return self.config.get("current-context")

    def get_generic(self, container: dict, name: str):
        for item in container:
            if item.name == name:
                return item
        raise KeyError(f"{name} not found", name)

    def get_context(self, context_name: str) -> dict:
        return self.get_generic(self.contexts, context_name)

    def get_cluster(self, cluster_name: str) -> dict:
        return self.get_generic(self.clusters, cluster_name)

    def get_user(self, user_name: str) -> dict:
        return self.get_generic(self.users, user_name)

    def get_auth_data(self, context_name: str = None) -> tuple:
        if context_name is None:
            context_name = self.current_context
        context = self.get_context(context_name)
        cluster_info = self.get_cluster(context.context.cluster)
        server = cluster_info.cluster.server
        user_info = self.get_user(context.context.user)

        # If token is found no need for certificates info
        token = user_info.user.get("token")
        if token:
            return server, token

        def create_tmp_file(data):
            if data:
                tmp_file = NamedTemporaryFile(delete=False)
                tmp_file.write(b64decode(data))
                tmp_file.close()
                return tmp_file.name

        client_ca_data = cluster_info.cluster.get("certificate-authority-data")
        client_key_data = user_info.user.get("client-key-data")
        client_cert_data = user_info.user.get("client-certificate-data")
        client_key_file = user_info.user.get("client-key")
        client_cert_file = user_info.user.get("client-certificate")
        client_ca_file = create_tmp_file(client_ca_data)
        client_key_file = client_key_file or create_tmp_file(client_key_data)
        client_cert_file = client_cert_file or create_tmp_file(client_cert_data)
        cert = (client_cert_file, client_key_file)
        return server, cert, client_ca_file
