# kubecfg

Python library and cli utility to check k8s client configurations


[![PyPi](https://img.shields.io/pypi/v/kubecfg.svg?style=flat-square)](https://pypi.python.org/pypi/kubecfg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/ambv/black)


Show configuration
![Features](https://github.com/joaompinto/kubecfg/raw/main/imgs/features.png)

Test connectivity
![Ping](https://github.com/joaompinto/kubecfg/raw/main/imgs/ping.png)

# Install
```sh
pip install kubecfg
```

# Run
```sh
kubecfg
```

# Use the library
This example shows how to use the [HTTPX](https://www.python-httpx.org/) to obtain the version of the API server.

```python
import httpx
from kubecfg.config import KubeConfig

k8s_config = KubeConfig()
k8s_config.load_config()

server, cert, client_ca = k8s_config.get_auth_data()
r = httpx.get(f"{server}/version", cert=cert, verify=client_ca)
r.raise_for_status()
print(r.text)
```
