# Physical restore approval gates

The current source proposal for [Portal #12](https://github.com/perkforge/perkforge-portal/issues/12)
uses `gitops/clusters/local` for an enabled physical source release candidate.
Only its local HelmRelease is unsuspended. Independent enrollment still pins
disabled v2.0.0 and remains suspended; no deployment is implied.
It pins the existing v0.3.0 image digest
`sha256:ae13143108562e9753eab40650cfcef4b53d8336e733adc6a94dbccabc0a2616`.
It does not deploy, release, create credentials, or redesign the application.

Before enrolling this activation candidate:

1. Publish and verify the app config release, then coordinate exact enrollment and
   platform release pins. Keep the ownership chain paused while preparing prerequisites.
2. Enrollment must supply scoped namespaces/accounts, admission and network policy,
   private GHCR pull Secret `portal-registry-existing`, OIDC Secret
   `portal-oidc-existing`, and public CA ConfigMap `portal-identity-ca`. Verify image
   admission and authenticated pull without exposing credentials.
3. Approve DNS/TLS/ingress for `portal.perkforge.home.arpa`, resolve Keycloak from
   tenant pods without hostAliases, and trust its public CA with TLS verification on.
   Register exact callback `https://portal.perkforge.home.arpa/auth/callback` and web
   origin `https://portal.perkforge.home.arpa` on confidential client `portal-local`.
   Preserve audience `portal-local` and the reviewed `platform-admins` server policy.
4. Verify physical worker labels/capacity and negative scheduling/security cases.
   The chart requires the worker label and excludes control-plane/master labels.
   Budget remains one Recreate replica, requests 25m/64Mi, limits 250m/192Mi.
5. Review and publish the app configuration, then coordinate the released enrollment
   pin and unpause through the approved Git rollout. No credentials, ESO readiness,
   DNS or live capacity are presumed by this source change. Then
   test health, TLS, intended admin login, unauthorized denial, logout/session behavior
   and runtime isolation. Offline renders do not prove these live acceptance gates.

Rollback/containment: pause the owning reconciliation chain first; use reviewed Git
pins and explicit enable/suspend settings. Do not roll back to VM endpoints or infer
permission to delete namespaces/secrets. A restart signs users out; Portal has no
persistent storage. Nextcloud and its transfer/configuration are outside this change.
CI/workflow settings remain unchanged. Run local checks even when hosted CI is paused:

```sh
helm lint bundles/portal/chart
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

## Historical VM/Fleet operations (not physical deployment instructions)

The following records describe older VM/Fleet releases only. Do not use their image,
identity, host mappings, namespace, credential names or activation state for physical
restoration; the physical contract above and `gitops/README.md` take precedence.

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

## Approved initial activation

The reviewed bundle now enables exactly one portal replica with the existing v0.2.0
immutable digest. Platform registration remains independently pinned and paused until
its activation change is merged. Identity/TLS/credentials and positive/negative server
dry-runs were verified first. GitLab remains disabled; successful Home-user login and
actual kubelet image pull are post-activation acceptance checks, not claimed results.
The reusable chart default remains disabled.
