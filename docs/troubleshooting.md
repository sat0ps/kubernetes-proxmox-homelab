# Troubleshooting

## Duplicate IP addresses after cloning

### Symptom

New VMs appeared with the same hostname and DHCP address.

### Cause

The cloned template had a populated machine identity.

### Resolution

Assign a unique hostname and regenerate the machine ID on each clone before treating it as a separate host.

---

## kubeadm command appeared to time out

### Symptom

`qm guest exec` stopped waiting while kubeadm continued running.

### Cause

The Proxmox guest-exec request can time out before a long-running guest process finishes.

### Resolution

Check the actual guest state before retrying the operation. Do not assume a guest-exec timeout means the command failed.

---

## Control plane initially NotReady

### Symptom

The node was visible but remained NotReady immediately after kubeadm init.

### Cause

No CNI had been installed yet.

### Resolution

Install and verify Calico. Kubernetes requires Pod networking before normal node readiness.

---

## CoreDNS remained Pending

### Cause

CoreDNS cannot start normally until a CNI is available.

### Resolution

Verify Calico Pods and node readiness.

---

## Pod CIDR overlapped the LAN

### Symptom

The initial configuration used `192.168.0.0/16` while the physical LAN was `192.168.1.0/24`.

### Risk

Pod routes can conflict with routes to physical hosts.

### Resolution

Reset the cluster and rebuild with `10.244.0.0/16`.

---

## kube-state-metrics Service could not be converted to NodePort

### Error

```text
spec.clusterIPs[0]: Invalid value: "None":
may not be set to 'None' for NodePort services
```

### Cause

The existing Service was headless:

```text
CLUSTER-IP: None
```

### Resolution

Leave the headless Service unchanged and create a second Service of type NodePort with the same selector.

---

## Prometheus metrics worked in a browser but queries failed in shell

### Symptom

Running `kube_pod_info` inside the Prometheus container returned:

```text
/bin/sh: kube_pod_info: not found
```

### Cause

`kube_pod_info` is a PromQL metric name, not a shell command.

### Resolution

Run the query in the Prometheus expression browser or through the HTTP API.
