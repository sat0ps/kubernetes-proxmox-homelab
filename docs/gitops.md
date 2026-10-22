# FluxCD GitOps

## Architecture

```text
GitHub (main)
    ↓ GitRepository source
Flux source-controller
    ↓ artifact
Flux kustomize-controller
    ↓ Kubernetes API
gitops-demo namespace: nginx Deployment + ClusterIP Service
```

Flux is installed at version `v2.9.6` with the standard source-controller,
kustomize-controller, helm-controller, and notification-controller components.
The cluster runs Kubernetes `v1.37.1`, which is within the current Flux support
range. Flux reconciles only `./clusters/homelab`; the repository root is never
used as a source path.

## Ownership boundaries

Initially Git owns only:

- the Flux `GitRepository` and `Kustomization` resources in `flux-system`;
- the `gitops-demo` Namespace;
- the pinned nginx Deployment and ClusterIP Service.

Proxmox VMs and networking, Calico, Kubernetes PKI, kubeadm configuration,
etcd, CoreDNS, kube-proxy, kube-state-metrics, node-exporter, and the external
Windows Prometheus/Grafana stack remain manually managed. Existing files in
`manifests/`, `monitoring/`, and `experiments/` are deliberately outside the
managed path.

## Reconciliation, rollback, and drift correction

The `homelab` GitRepository polls `main` every minute. The matching Flux
Kustomization applies `clusters/homelab`, waits for readiness, and prunes only
resources declared by that path. A Git commit is therefore the change record:
edit the manifest, commit, push, wait for reconciliation, and verify the live
state. Reverting the commit rolls the cluster back. Manual changes to managed
objects are temporary and are corrected on the next reconciliation.

## Useful commands

```bash
flux get all -A
flux get sources git -A
flux get kustomizations -A
kubectl get pods -n flux-system
kubectl logs -n flux-system deploy/source-controller
kubectl logs -n flux-system deploy/kustomize-controller
kubectl logs -n flux-system deploy/helm-controller
kubectl logs -n flux-system deploy/notification-controller
flux reconcile source git homelab -n flux-system
flux reconcile kustomization homelab -n flux-system --with-source
```

## Pause and resume

```bash
flux suspend source git homelab -n flux-system
flux suspend kustomization homelab -n flux-system
flux resume source git homelab -n flux-system
flux resume kustomization homelab -n flux-system
```

Suspension changes live state and is not a Git commit. Confirm the object is
resumed after maintenance.

## Troubleshooting

1. Check `flux get all -A` and inspect the `Message` field.
2. Check `GitRepository/homelab` for fetch or authentication errors.
3. Check the kustomize-controller logs for build, validation, or apply errors.
4. Validate the path locally with `kubectl kustomize clusters/homelab`.
5. Confirm the Git commit exists on `main` and that the source revision moved.

If Flux is unavailable, repair the source/controller path and let
reconciliation restore the managed workload rather than applying it manually.
