# Inactive preview and approval gates

No deployment or image exists from this change. Do not apply the rendered output.
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
