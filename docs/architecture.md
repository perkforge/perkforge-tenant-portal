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

The runtime uses an existing unprivileged `portal-runtime` service account without
API token mount, UID/GID1000, read-only root, no capabilities and RuntimeDefault
seccomp. A single replica with Recreate matches process-local sessions. No storage
or database is needed. Proposed 25m/64Mi request and 250m/192Mi limits require actual
capacity/load validation before adoption, not an assumption of available memory.

The pod explicitly binds 0.0.0.0:3000 inside its namespace. It must be reachable
only through separately approved internal HTTPS ingress with narrow NetworkPolicy;
no public DNS or LoadBalancer/NodePort is created. Secure cookies remain mandatory.

## Platform identity connection

Fleet reads non-secret Helm values from platform-owned ConfigMap
`tenant-home-portal/portal-platform-values`, key `values.yaml`, through the bundle's
`helm.valuesFrom`. This repository does not create or mutate that ConfigMap. Missing
configuration fails Fleet rendering. Platform supplies the issuer/client/audience,
origin, image selection and Secret reference; the client secret stays in a separate
operator-managed Secret and is never included in Helm values.

Values precedence is not authorization. Tenant-controlled charts can change values
or remove the reference. Platform-owned admission therefore validates the actual
workload image, environment, Secret reference, service account and injection paths.
The runtime cannot be trusted to authorize future privileged platform operations
merely because configuration was supplied by platform; independent authorization
is required. Platform's default config keeps this chart disabled and the GitRepo
paused. No service or security control is activated by this connection.
