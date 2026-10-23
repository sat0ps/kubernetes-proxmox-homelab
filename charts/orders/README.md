# Orders Helm chart

One reusable chart renders the Orders frontend and API for both the Proxmox Kubernetes environment and Azure AKS.

## Validation

```bash
helm lint ./charts/orders
helm lint ./charts/orders -f ./charts/orders/values-onprem.yaml
helm lint ./charts/orders -f ./charts/orders/values-aks.yaml
helm template orders ./charts/orders -f ./charts/orders/values-onprem.yaml
helm template orders ./charts/orders -f ./charts/orders/values-aks.yaml
```

The chart references an existing Kubernetes Secret for `DATABASE_URL`; it does not store database credentials. PostgreSQL deployment and persistence are intentionally deferred to the storage issue.

The environment values files contain only differences from the shared defaults. No duplicated Deployment manifests are maintained.
