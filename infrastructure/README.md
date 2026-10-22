# Infrastructure ownership boundary

This directory is reserved for future, explicitly scoped infrastructure
resources. The initial Flux installation does not manage Proxmox VMs, node
networking, Calico, Kubernetes PKI, etcd, CoreDNS, kube-proxy, or the external
Prometheus/Grafana stack.

Existing infrastructure manifests under `manifests/` remain documentation and
manual-operation material until a separate migration is planned and approved.
