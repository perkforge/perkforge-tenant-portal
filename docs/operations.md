# Inactive preview and approval gates

No deployment exists from this change. The application values pin the Actions-published
v0.2.0 image; enabled remains false. Do not apply the rendered output.
With Helm3 and Python3/PyYAML installed, run:

```
helm lint bundles/portal/chart
python3 -m unittest discover -s tests -v
```

Tests render offline using synthetic digest/host/secret names and assert default
inactivity, required configuration, namespaced ownership and runtime hardening.
The fixture image digest is never a deployment recommendation. No chart dependencies
are downloaded. No Docker, cluster or external identity/GitLab calls are necessary.

Before activation: inspect fresh lab capacity; approve namespace/project/budget and
network controls; build and scan the application image then pin its verified digest;
review TLS hostname/ingress; provision a narrow OIDC confidential client with exact
callback URI, API audience, tenant-reader role and Home group mapping; securely
create its referenced secret; then review/pin this repository's exact commit in a
scoped paused platform GitRepo. Approve enablement and unpause separately. Never
resume paused Keycloak just to exercise this chart. GitLab remains disabled.

Liveness/readiness report process availability, not identity or GitLab health.
Restart/rollout signs users out; no persistent data exists. Roll back by an approved
Git pin change; do not infer authorization to uninstall or delete Home resources.

References: https://fleet.rancher.io/reference/ref-fleet-yaml and
https://helm.sh/docs/chart_template_guide/values_files/ .

For an offline application preview, use `-f bundles/portal/values.yaml` with ordinary
`helm template`, the selected namespace, and a synthetic digest only in tests. No
platform ConfigMap lookup is required. The platform repo separately validates these
inputs and enforces its runtime constraints; passing chart tests is not deployment
approval or proof of live enforcement. Fleet release-storage permissions remain an
activation gate owned outside this application repository.

## Prepared image pin

Release: [v0.2.0](https://github.com/perkforge/perkforge-portal/releases/tag/v0.2.0).
Source: `97efc86121e3f121e852f54e6b65665a7d68acec`.
[Main Actions run 40586703759](https://github.com/perkforge/perkforge-portal/actions/runs/40586703759)
published both the version and full-SHA tags with manifest digest
`sha256:2e07afbb31fd462911a365893d05796090883464560478bd70179466af5b17b7`.
This is the registry artifact, not the earlier locally preloaded image.

The package must remain private. The application references only the existing
`portal-ghcr` imagePullSecret in its release namespace; the platform provisions and
rotates its credential separately. No Secret object or credential belongs in this
repository. Authenticated pull verification remains an activation gate, requiring
separate credential-provisioning approval. The runtime does not mount this Secret;
the kubelet uses it for registry authentication. Production JS dependencies passed
npm audit and the image passed an isolated smoke check; no OS vulnerability scan or
live OIDC integration is claimed. Platform image admission and tenant values must pin
this same digest. Merging alone must not enable portal.

## Local identity CA

The reviewed local values reference an existing public CA ConfigMap, `portal-identity-ca`,
and map only `keycloak.local-lab.test` to the current internal ingress Service address
`10.43.163.193`. These are ordinary runtime inputs; the chart creates no CA, credentials,
DNS server or policy. Platform independently validates the exact mount, environment
and host mapping. Revalidate the address if the ingress Service is recreated.
Node loads `/etc/portal/identity-ca/ca.crt` through `NODE_EXTRA_CA_CERTS`; TLS verification
remains enabled. No private CA key is mounted. Restart the application after CA rotation.
The bundle remains disabled until operator credential, ingress and identity checks pass.
