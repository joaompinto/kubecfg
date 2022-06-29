kpet get "api/v1/pods" -pf "{name} is using IP {_.status.podIP}"
kpet get "api/v1/nodes" -pf "{name}\n\t{_.status.capacity}"

kpet get api/v1/namespaces
