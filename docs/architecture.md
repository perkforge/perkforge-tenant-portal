# Repository ownership

- `perkforge-portal`: React/Node source, authentication, API, tests and image build.
- `perkforge-tenant-portal`: local Helm chart, Fleet bundle and tenant app configuration.
- `perkforge-platform`: Home namespace/project/quota/security, runtime service account,
  trusted TLS ingress, dedicated Fleet workspace/policy/mapping and GitRepo registration.

This follows the Nextcloud application/platform ownership division, with portal
source kept separately from its tenant deployment repository.

`bundles/portal/fleet.yaml` uses the local `chart/` and defaults to disabled through
`values.yaml`. The chart also defaults disabled, rendering no objects. Enabled
rendering requires an immutable image digest, exact HTTPS origin, HTTPS identity
issuer, audience/client IDs and an existing operator-managed secret reference.
Only Deployment and ClusterIP Service render; no namespace, Secret, RBAC,
NetworkPolicy, ingress or cluster-scoped object is managed by this repository.

The runtime references the existing unprivileged `serviceAccount.name` input without
API token mount, UID/GID1000, read-only root, no capabilities and RuntimeDefault
seccomp. A single replica with Recreate matches process-local sessions. No storage
or database is needed. Proposed 25m/64Mi request and 250m/192Mi limits require actual
capacity/load validation before adoption, not an assumption of available memory.

The pod explicitly binds 0.0.0.0:3000 inside its namespace. It must be reachable
only through separately approved internal HTTPS ingress with narrow NetworkPolicy;
no public DNS or LoadBalancer/NodePort is created. Secure cookies remain mandatory.

## Application inputs and external enforcement

`bundles/portal/values.yaml` supplies ordinary application settings: origin,
issuer/client/audience, an existing client-secret reference, and an existing runtime
service account. No secret value belongs in Git. Image approval and enablement remain
separate steps. Release namespace is supplied at deployment; the chart does not know
how its namespace, quota, policies or service account were created.

The downstream Fleet bundle has no platform-values ConfigMap lookup, platform routing
labels, or foundation component switches. It owns only its application deployment.
Platform independently constrains the deployed image, environment, Secret/service-account
references and injection paths. Application values are a request, not authorization;
changing them does not grant a capability. Cross-repository tests compare those inputs
with the platform's approved runtime contract. This intentional comparison replaces
hidden configuration injection.

Future privileged APIs must independently authorize operations. A tenant-controlled
application is not made trustworthy by its configuration or by being a household app.
