from .config import KubeConfig


def main():
    kubeconfig = KubeConfig()
    kubeconfig.load_config()
    kubeconfig.show_clusters()
    kubeconfig.show_contexts()
    kubeconfig.show_users()
    kubeconfig.show_current()


if __name__ == "__main__":
    main()
