# Orders on-prem GitOps release

Flux reconciles this directory from `main`.

The `HelmRelease` consumes the reusable chart in `charts/orders` with `values-onprem.yaml`. The application database URL is supplied through a Kubernetes Secret reference and contains no password.

## Temporary database baseline

Issue #5 needs a healthy source application before the dedicated persistence work in #7. PostgreSQL is therefore GitOps-managed here as a single-replica **ephemeral baseline** using host authentication without a password. It is reachable only as a ClusterIP service and is not the final persistence/security design.

Issue #7 must replace this temporary database lifecycle with durable Kubernetes storage and production-appropriate credential handling.

## Ownership

Git/Flux owns the resources in this directory and the Helm release. Normal changes must be made through Git rather than direct `kubectl apply` or `helm upgrade`.
