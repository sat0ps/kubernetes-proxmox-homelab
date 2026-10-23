# Orders GitOps deployment incident and recovery

## Context

Issue #5 established the Orders application as the healthy on-premises source environment on the Proxmox Kubernetes cluster. Flux owns the release through Git and the reusable `charts/orders` Helm chart.

## Incident

The initial Flux Helm installation did not become healthy because the frontend Pods entered `CrashLoopBackOff`. nginx could not resolve the Kubernetes API Service name:

```text
host not found in upstream "orders-orders-api"
```

The frontend NetworkPolicy allowed application egress to the API on TCP/8000 but did not allow DNS egress. The API policy already had DNS access.

## First fix: DNS egress

PR #23 added UDP/53 and TCP/53 egress for the frontend. No live NetworkPolicy patch was applied.

After merge, the GitRepository observed the corrected Git revision, but the live NetworkPolicy remained unchanged.

## Deeper cause: stale HelmChart artifact

The Helm chart was configured with `reconcileStrategy: ChartVersion`. The chart source changed in Git, but the chart version remained `0.1.0+1`. Flux therefore continued to use the previously packaged HelmChart artifact.

This demonstrated that GitRepository reconciliation, HelmChart artifact reconciliation, HelmRelease reconciliation, and workload health are separate layers of Flux state.

## Second fix: reconcile by Git revision

PR #24 changed the Orders HelmRelease to:

```yaml
reconcileStrategy: Revision
```

No chart-version bump was combined with this change, so recovery directly demonstrated the intended reconciliation behavior.

Flux rebuilt the chart as:

```text
orders@0.1.0+08e58c3eba45.2
```

The live frontend NetworkPolicy then contained TCP/8000, UDP/53, and TCP/53. The frontend recovered to 2/2 Ready, the API remained 2/2 Ready, and PostgreSQL remained 1/1 Ready.

The HelmRelease retained its previous failed upgrade condition until its exhausted reconciliation state was reset and reconciliation requested. It then completed successfully:

```text
READY=True
Helm upgrade succeeded for release orders/orders.v4
with chart orders@0.1.0+08e58c3eba45.2
```

## Engineering decisions

- The live Kubernetes objects were not manually patched to repair the defect.
- The desired-state fixes were made in Git and delivered through Flux.
- `Revision` is used because this repository treats Git commits as the deployment source of truth for the local chart.
- PostgreSQL remains an intentionally ephemeral baseline until the dedicated persistence work in issue #7.

## Lessons

1. A current Flux GitRepository does not prove that a Git-sourced Helm chart artifact has been rebuilt.
2. NetworkPolicy egress restrictions must account for DNS when workloads resolve Kubernetes Services.
3. HelmRelease conditions can preserve failure/remediation state after workloads have recovered and should be inspected independently.
4. GitOps recovery should repair desired state in Git rather than bypassing reconciliation with live patches.

## Evidence trail

- Issue #5: Orders deployment to Proxmox Kubernetes through Flux and Helm
- PR #22: initial Orders Flux/Helm deployment
- PR #23: frontend DNS egress correction
- PR #24: Helm chart reconciliation changed from chart-version-driven to Git-revision-driven
- Final observed workload state: frontend 2/2 Running, API 2/2 Running, PostgreSQL 1/1 Running
- Final HelmRelease state: Ready=True
