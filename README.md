# Kubernetes Python Exploration Tool

Command line tool to explore the Kubernetes API using Python expressions

[![PyPi](https://img.shields.io/pypi/v/kpet.svg?style=flat-square)](https://pypi.python.org/pypi/kpet)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/ambv/black)

# Motivation

Explore the [Kubernetes API] by using «k8s tailored» REST client while supporting Python expressions for formatting and filterting data.

[Kubernetes API]: https://kubernetes.io/docs/reference/kubernetes-api/


# Install
```sh
pip install kpet
```

# Usage examples

Show the current kubernetes context configuration (detected from your KUBECONFIG file)
```sh
kpet show
```

List all the API endpoints
```sh
kpet get
```

Get the kubernetes API server version
```sh
kpet get version
```


Get the list of nodes
```sh
kpet get api/v1/nodes
```

Get the PodIP for all pods, check the [special symbols](doc/symbols.md) for other symbols.
```sh
kpet get api/v1/pods -f "{name} is using IP {_s.podIP}"
```

Print the names of all running pods
```sh
kpet get api/v1/pods -f"{name}" -s "_s.phase=='Running'"
```

Print the names of all nodes which are Ready
```sh
kpet get api/v1/nodes -f"{name}" -s "[c for c in _s['conditions'] if c.type=='Ready' and c.status=='True']"
```
