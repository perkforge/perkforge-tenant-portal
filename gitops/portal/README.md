# Paused Flux application entrypoint

This is an optional tenant-owned app entrypoint at `gitops/portal`; it does not
change the existing Fleet deployment or authorize switching controllers.
The chart remains `bundles/portal/chart` (`household-portal` 0.1.0), referenced
from the same repository rather than copied. Values default to disabled and
HelmRelease/portal is suspended. No image, credential or activation is approved.

Platform-owned enrollment must create a pinned `GitRepository/tenant-portal`
and a scoped Flux Kustomization targeting this path in a separately approved
tenant namespace. Its `spec.serviceAccountName` is the platform-supplied tenant
reconciliation identity. That identity may apply only approved tenant app
resources and cannot edit platform enrollment, identities, policy or Big Bang.
Flux supplies the namespace through the parent Kustomization's targetNamespace;
this repository creates no Namespace, ServiceAccount, RBAC, Secret or policy.

The child HelmRelease uses `spec.serviceAccountName: portal-deployer`, a separate
platform-supplied scoped identity. `storageNamespace` names separately provisioned
isolated Helm storage; the runtime account is `portal-runtime`. These names are
illustrative contracts, not created grants. Platform RBAC/admission must constrain
allowed release/source refs, impersonation, target/storage namespaces, runtime,
image and secret references. Missing prerequisites must fail closed, never fall
back to a broad account. Tenant configuration alone grants no capability.

Before live use, review/pin the source revision, namespace and storage allocation,
identity/RBAC/admission/network/TLS, actual image/secret references, capacity and
recovery; approve activation separately. Do not let Fleet and Flux manage the
same release or workloads. No live migration, provisioning or reconciliation
was performed. The application source repository is unchanged.

Offline checks from repo root, with existing tools:

```sh
kubectl kustomize gitops/portal > /tmp/portal-flux.yaml
helm lint bundles/portal/chart -f gitops/portal/values.yaml
helm template portal bundles/portal/chart -f gitops/portal/values.yaml > /tmp/portal-disabled.yaml
python3 -m unittest discover -s tests -v
```

The default chart render must contain no workloads. Local build/schema checks
cannot prove live API authorization, session revocation or tenant isolation.

The separate platform-owned
[enrollment repository](https://github.com/perkforge/perkforge-platform-tenants)
selects this entrypoint explicitly per cluster. It owns the source pin and scoped
parent reconciler; this repository owns the app release and values. Companion
PRs use exact feature-commit pins for review only. Merge this app-entrypoint PR
first, then advance the enrollment pin to the approved merged commit; enrollment
merges next, and platform root references advance last. Revalidate each new pin.
A merge does not unsuspend or authorize any deployment.
