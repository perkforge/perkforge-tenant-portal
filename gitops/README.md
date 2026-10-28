# Paused tenant app: shared → environment → profile → cluster

This optional Flux layout owns only the portal application. The existing Fleet
bundle and `bundles/portal/chart` (`household-portal` 0.1.0) are unchanged; no
chart or generated workload YAML is copied. Every release stays suspended and
shared app values keep `enabled: false`. Start from a named cluster root, never
apply `shared/` alone.

```text
shared/                    # one app release + shared values
  release.yaml             # chart ref and explicit ordered valuesFrom
  values.yaml
  kustomization.yaml
environments/{local,dev}/   # small reusable app values only
profiles/{il2,il5}/         # illustrative app audience inputs, not security controls
clusters/{local,dev-il2,dev-il5}/
  kustomization.yaml       # selects shared + one environment
  values.yaml              # only this cluster's overrides (may be empty)
```

Cluster identity and environment are independent. `dev-il2` and `dev-il5`
explicitly select the same `environments/dev` input but have different illustrative
origins and profile choices (`il2` and `il5`). `local` selects `environments/local`. These aliases do not imply hosting,
Kubernetes distribution or security/impact level; none of those platform settings
belongs in this app repository.

`shared/release.yaml` consumes `portal-defaults`, then `portal-environment`,
`portal-profile`, and `portal-cluster`. Each ConfigMap carries a `values.yaml` key. **Later values win**;
chart defaults precede all three. Maps merge and lists replace. No inline
`spec.values` adds a hidden override. Example: environment dev supplies issuer
and client ID; the app profile selects an illustrative audience, the cluster
changes only origin, and the shared secret-name
reference remains. Endpoints/client IDs are `.invalid` examples, not approved
OIDC registrations or shared credentials. Review real per-cluster clients,
callbacks, secret references and image pins before enablement.

## Explicit cross-repository selection

| Cluster identity | Environment | Profile | App audience example |
| --- | --- | --- | --- |
| local | local | il2 | example-portal-il2 |
| dev-il2 | dev | il2 | example-portal-il2 |
| dev-il5 | dev | il5 | example-portal-il5 |

The native Kustomize `commonAnnotations` fields `example.perkforge.io/cluster`,
`environment`, and `profile` make the selected context visible on built Flux
objects. The platform selects a named cluster/environment/profile; enrollment
records the same context and selects the same app cluster root. Tests compare
all three pinned repositories, the actual source paths and selected environment/
profile inputs. This is an explicit checked contract, not magical propagation.

App profiles contain a real supported chart input (`identity.audience`) to show
how profile-specific app settings compose. The `.invalid` identity endpoints
and `example-*` audiences are illustrative only, not IL2/IL5 policy requirements,
approved identity registrations or evidence of authorization. Real app differences
need review; these files cannot configure or weaken platform RBAC, namespace,
NetworkPolicy, admission or other security controls. Context annotations are
untrusted app claims checked against platform Git, not security enforcement.

## Add a cluster

Copy the small `clusters/dev-il5/` directory to a unique cluster name,
select the desired existing environment/profile in its `kustomization.yaml`,
update its cluster context annotation, and edit
only its app overrides. Reuse environment values rather than copying them.
Then platform enrollment must explicitly select `./gitops/clusters/<name>` in
its pinned source; adding a directory here enrolls nothing automatically. Both dev examples share environment defaults but select separate profiles. The
companion enrollment must explicitly opt in to every named cluster.

## Platform boundary and review pins

The separate [platform-owned enrollment repository](https://github.com/perkforge/perkforge-platform-tenants)
creates `GitRepository/tenant-portal` and a scoped Flux Kustomization targeting
one named-cluster path in a separately approved tenant namespace. Its service
account applies only approved app release/config objects. This repository creates
no Namespace, ServiceAccount, RBAC, Secret, policy or platform enrollment.

The app HelmRelease uses `spec.serviceAccountName: portal-deployer`, separate
`storageNamespace: tenant-example-portal-release`, and runtime `portal-runtime`.
These are unprovisioned platform contracts. Platform RBAC/admission must constrain
source/identity/target/storage/secret/image fields; app values grant no capability.
The parent supplies the runtime namespace through targetNamespace. Missing
prerequisites must fail closed, never fall back to a broad account.

Companion pins are exact feature commits for review only, not production refs.
Merge app first, then advance/revalidate enrollment's app pin; merge enrollment,
then advance/revalidate platform's enrollment pin. Merge does not unsuspend.
Live identity/RBAC/admission/network/TLS, capacity, credentials, recovery and
controller handoff remain separately approved. Never let Fleet and Flux own the
same release/workloads. The application source repository is unchanged.

## Offline checks

```sh
kubectl kustomize gitops/clusters/local > /tmp/portal-local.yaml
kubectl kustomize gitops/clusters/dev-il2 > /tmp/portal-dev-il2.yaml
kubectl kustomize gitops/clusters/dev-il5 > /tmp/portal-dev-il5.yaml
python3 -m unittest discover -s tests -v
```

Tests feed actual assembled ConfigMap references to the existing chart in the
release's valuesFrom order. Default renders emit no workloads. Synthetic enabled
renders verify two clusters sharing dev, il2/il5 audience composition, override precedence, inherited settings,
adding another cluster, environment/profile/target mismatch rejection and failed
activation without a digest; fixture values
are not deployment recommendations. Output stays temporary. No API calls or
live tenant isolation/readiness claims result from these checks.
