from kubecfg.config import KubeConfig


def show():
    """ show the kubeconfig """
    kubeconfig = KubeConfig()
    kubeconfig.load_config()
    kubeconfig.show_clusters()
    kubeconfig.show_contexts()
    kubeconfig.show_users()
    kubeconfig.show_current()
