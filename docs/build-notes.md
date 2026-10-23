# Build Notes

## Final cluster state

| Node | Role | Address |
|---|---|---|
| k8s-control-01 | control-plane | 192.168.1.139 |
| k8s-worker-01 | worker | 192.168.1.192 |
| k8s-worker-02 | worker | 192.168.1.134 |

- Kubernetes: v1.37.1
- Ubuntu: 22.04.5 LTS
- containerd: 2.2.1
- CNI: Calico 3.33
- Pod CIDR: 10.244.0.0/16
- Monitoring: Prometheus and Grafana on Windows Docker Desktop
- Linux metrics: node-exporter on TCP/9100
- Kubernetes object metrics: kube-state-metrics through NodePort 30080

## Persistent node addresses

The Kubernetes VMs use persistent static addresses inside the guests:

| VM | Hostname | Address |
|---:|---|---|
| 150 | k8s-control-01 | 192.168.1.139/24 |
| 151 | k8s-worker-01 | 192.168.1.192/24 |
| 152 | k8s-worker-02 | 192.168.1.134/24 |

Each guest has `/etc/netplan/99-k8s-static.yaml` with gateway
`192.168.1.1` and DNS `192.168.1.1`. Cloud-init network regeneration is
disabled with `/etc/cloud/cloud.cfg.d/99-disable-network-config.cfg`, so a
shutdown or reboot does not replace the static configuration with a new DHCP
lease. Proxmox bridges and VM disks remain unchanged.

## VM preparation

Three VMs were cloned from an Ubuntu cloud-init template.

The clones initially inherited the same hostname and machine identity. The hostnames were changed to:

```text
k8s-control-01
k8s-worker-01
k8s-worker-02
```

Machine IDs were regenerated so DHCP and system identity were unique.

## Kernel and networking prerequisites

Swap was disabled.

Required modules:

```text
overlay
br_netfilter
```

Required sysctls:

```text
net.bridge.bridge-nf-call-iptables=1
net.bridge.bridge-nf-call-ip6tables=1
net.ipv4.ip_forward=1
```

## Container runtime

containerd was installed on all nodes.

The default configuration was generated and systemd cgroups were enabled:

```text
SystemdCgroup = true
```

## Kubernetes packages

The following components were installed and held at v1.37.1:

- kubeadm
- kubelet
- kubectl

## Control-plane bootstrap

The final kubeadm initialisation used:

```bash
kubeadm init \
  --apiserver-advertise-address=192.168.1.139 \
  --pod-network-cidr=10.244.0.0/16
```

The initial attempt used an overlapping Pod CIDR and was reset before the final bootstrap.

## Calico

Calico was deployed after kubeadm.

Once Calico became healthy:
- the control-plane node changed to Ready
- CoreDNS moved from Pending to Running
- worker nodes became fully operational after joining

## Monitoring

node-exporter was installed on all three Linux nodes and exposed on port 9100.

kube-state-metrics was deployed into Kubernetes.

Because the standard Service is headless, a second Service exposes the metrics endpoint on NodePort 30080.

Prometheus then scrapes:
- all three node-exporter endpoints
- kube-state-metrics

Grafana uses the same Prometheus datasource for all panels.

## Security

This repository intentionally excludes:
- kubeadm bootstrap tokens
- kubeconfig files
- private keys
- passwords
- Grafana credentials
- Prometheus credentials
