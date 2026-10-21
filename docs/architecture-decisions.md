# Architecture Decisions

## 1. kubeadm instead of a packaged Kubernetes distribution

The cluster was intentionally built with kubeadm, kubelet, kubectl, and containerd so the control-plane bootstrap process, PKI, static Pods, CNI dependency, and node joining process could be observed directly.

## 2. Separate physical and Pod address spaces

The physical LAN uses `192.168.1.0/24`.

The first bootstrap attempted to use `192.168.0.0/16` for Pods. That range contains the physical LAN and therefore created an overlap risk.

The cluster was reset and rebuilt with:

```text
Node network: 192.168.1.0/24
Pod network:  10.244.0.0/16
```

This avoids ambiguous routing between physical hosts and Pods.

## 3. Calico with VXLAN

Calico is used as the CNI.

For this lab:
- VXLAN encapsulation is enabled
- BGP is disabled
- outgoing NAT is enabled
- Pod CIDR is `10.244.0.0/16`
- IPAM block size is `/26`

VXLAN is appropriate here because it provides cross-node Pod connectivity without requiring the home network to understand Pod routes.

## 4. External monitoring stack

Prometheus and Grafana were already running in Docker Desktop on a separate Windows system.

Instead of replacing that stack, the Kubernetes cluster exports metrics to it.

This demonstrates a useful operational boundary:

```text
Kubernetes nodes
   ↓
metric exporters
   ↓
external Prometheus
   ↓
Grafana
```

## 5. Separate exporters for separate concerns

`node-exporter` provides Linux OS and hardware-level metrics.

`kube-state-metrics` provides Kubernetes object state.

These are intentionally treated as different data sources because they answer different questions.

## 6. NodePort for kube-state-metrics

The default kube-state-metrics Service is headless.

Since Prometheus runs outside the cluster, a second NodePort Service exposes only the metrics endpoint on port `30080`.

This is acceptable for a controlled homelab network. A production design would normally use authenticated service discovery, an in-cluster Prometheus, a private load balancer, or another controlled scrape path.

## 7. Control-plane scheduling

The control-plane node keeps the normal `NoSchedule` taint for application workloads.

This keeps normal workload scheduling focused on the two workers while system components remain on the control plane.
