kubecfg get "api/v1/pods" -pf "{name} is using IP {_.status.podIP}"
kubecfg get "api/v1/nodes" -pf "{name}\n\t{_.status.capacity}"
