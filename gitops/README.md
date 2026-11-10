# Paused portal: shared → environment → profile → cluster

Start at `clusters/local/kustomization.yaml` or `clusters/dev/kustomization.yaml`.
Local now means the physical home platform; dev remains an inactive example. Both select il2.
Published v1.0.0 and legacy Fleet inputs retain their historical VM meaning.
This is a breaking configuration contract: local endpoints, placement and activation
state change. Consumers must coordinate compatible releases rather than treat it as
a drop-in v1 patch; preserve the breaking classification when squash-merging.
Cluster identity, environment and profile remain independent inputs.

```text
shared/                   # one chart reference/release + disabled defaults
environments/{local,dev}/  # reusable app settings
profiles/il2/             # illustrative app input
clusters/{local,dev}/      # explicit entrypoints and final overrides
```

- `environments/{local,dev}/values.yaml`: reusable client-name examples.
- `profiles/il2/values.yaml`: illustrative supported `identity.audience` input.
- `clusters/{local,dev}/kustomization.yaml`: explicit shared/environment/profile selection.
- `clusters/{local,dev}/values.yaml`: per-cluster origin and issuer.

The existing `bundles/portal/chart` (`household-portal` 0.1.1) is referenced, not
copied. Legacy Fleet behavior is unchanged. Helm `valuesFrom` order is
`portal-defaults` → `portal-environment` → `portal-profile` → `portal-cluster`.
Later values win; maps merge and lists replace; no inline values hide another layer.

| Target | Environment / profile | Origin | Issuer |
| --- | --- | --- | --- |
| local | local / il2 | https://portal.perkforge.home.arpa | https://keycloak.perkforge.home.arpa/auth/realms/perkforge |
| dev | dev / il2 | https://portal-dev-il2.local-lab.test | https://keycloak-dev-il2.local-lab.test/realms/household |

These are configurable test-host contracts, not configured DNS/TLS or registered
clients. The application callback is `<origin>/auth/callback`; register that exact
URI and approved web origin later. The chart consumes `portalOrigin` and
`identity.issuer/clientId/audience/existingSecret`; it creates no ingress or
identity client. Platform enrollment owns routing/TLS and secret provisioning.
The realm, client names and audience need review, as do the approved image digest
and existing secret/account references. No live identity changes are included.

Local now proposes explicit `platform-admins` server policy with client/audience
`portal-local`; Home group defaults stay in `dev`/legacy configuration. Missing
policy or malformed settings fail closed. Local pins the published v0.3.0 image
digest verified from the successful source/version registry push records. GHCR
remains private: `portal-registry-existing` needs separately approved read-only
pull credentials. Anonymous pulls were refused; no credential is provisioned here.
All Flux selections remain disabled/suspended until separate activation approval.
ConfigMaps and HelmRelease are applied in `tenant-portal-config`, while the release
targets `tenant-portal` and stores history in `tenant-portal-release`. Runtime never
mounts deployer/reconciler tokens. Platform enrollment owns those boundaries.

## Add or change an input

- **Cluster:** copy `clusters/dev/`, update its cluster annotation, selected environment/profile
  and values. Enrollment must explicitly select `./gitops/clusters/<name>`.
- **Environment:** add a small `environments/<name>/` values/Kustomization pair,
  select it in the cluster root, and update the environment annotation.
- **Profile:** add `profiles/<name>/` only for real supported app differences;
  update the selection and annotation. Future il5 is guidance only, not supplied
  configuration or an authorization claim. App settings cannot relax platform controls.

Several clusters can reuse `environments/dev` without copying it. Adding a folder
enrolls nothing. Matching cluster/environment/profile annotations are checked
against protected platform/enrollment Git at exact pins; they do not enforce security.

## Ownership and review order

Platform-owned `perkforge-platform-tenants` enrolls this source under scoped
identities. This app Git creates only ConfigMaps and a paused HelmRelease: no
Namespace, ServiceAccount, RBAC, policy, Secret or Big Bang configuration.
`portal-deployer`, `portal-runtime`, isolated Helm storage and parent
`portal-reconciler` are unprovisioned reviewed contracts. Missing prerequisites
must fail closed; no broad fallback is allowed. Foundation/admission must constrain
identities, namespaces, sources, secrets and images before activation.

Release the reviewed app configuration first, then update and validate the enrollment
release, then the platform release. Use only actual published immutable release refs.
Squash/rebase changes SHAs. Review pins are not production refs. Merge never unsuspends.

## Offline checks

```sh
kubectl kustomize gitops/clusters/local > /tmp/portal-local.yaml
kubectl kustomize gitops/clusters/dev > /tmp/portal-dev.yaml
python3 -m unittest discover -s tests -v
```

Tests render the actual ordered ConfigMaps through the existing chart. Disabled
renders emit no workloads. Synthetic enabled renders check origins/issuers,
precedence, shared dev reuse, mismatch rejection and missing-digest rejection.
No generated YAML is committed. Live capacity, credentials, OIDC/RBAC/admission,
network/TLS, tenant denials, controller ownership and recovery remain separate
approval gates. Fleet and Flux must never own the same workloads.


## Physical local selection

Reuse `clusters/local` to match the physical platform's existing local/environment/il2
selection. This avoids adding a second competing target. Older released tags are not
rewritten. This proposal explicitly sets `enabled: false` and inherits suspension;
shared/dev and legacy Fleet inputs stay unchanged. Publishing it cannot authorize
activation. Never enroll the historical Fleet bundle on the physical cluster.

The proposed origin is `https://portal.perkforge.home.arpa` and exact callback is
`https://portal.perkforge.home.arpa/auth/callback`. The issuer is
`https://keycloak.perkforge.home.arpa/auth/realms/perkforge`; client and audience stay
`portal-local`, with explicit `platform-admins` policy. Platform-owned DNS must resolve
Keycloak normally: there is no static VM hostAlias. Worker selection requires
`storage.perkforge.io/worker=true` and excludes both control-plane/master role labels;
no tolerations permit control-plane scheduling. Verify worker labels before activation.

One stateless Recreate replica keeps requests 25m/64Mi and limits 250m/192Mi.
Runtime, Helm control and history namespaces remain `tenant-portal`,
`tenant-portal-config` and `tenant-portal-release`. No credentials, identity clients,
TLS ingress, security controls or runtime authorities are created here.
See [physical approval gates](../docs/operations.md#physical-restore-approval-gates).

Selection annotations use `platform.perkforge.io/cluster`, `/environment` and `/profile`. Consumers must select a compatible published configuration release; older releases are not rewritten. This metadata change does not enable the application or grant platform authority.
