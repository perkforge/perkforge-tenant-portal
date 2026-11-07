# Household portal tenant deployment

This repository owns only namespaced portal application deployment configuration.
Read gitops/README.md, docs/architecture.md and docs/operations.md. Big Bang/Flux is
the active platform. Use gitops/ for Flux application configuration; Fleet/VM
instructions in older docs and bundles are historical, not a supported physical
deployment path. Application source/image build is in perkforge-portal.
Platform/enrollment Git owns namespaces, quotas, runtime service accounts, RBAC,
network policy, TLS ingress and source registration. Keep enabled=false until
separate deployment approval. Never apply manifests, provision secrets/identity,
expand privileges, or enable paused services without authorization. No main pushes,
force pushes or merges. Never commit secrets, local evidence or fixture credentials.

## Working rules

- Use the GitHub CLI (`gh`) for PerkForge GitHub operations unless Corey directs otherwise. Do not switch tools or credentials to bypass an access denial.
- Use the [Current Board](https://github.com/orgs/perkforge/projects/1/views/1) as authoritative for work scope, priority and status. Check the relevant issue before starting or proposing the next task.
- Keep tickets and PR/MR descriptions concise: outcome, blocker or next action, and relevant evidence links. Avoid repeated narration.
- Work on feature branches and submit draft PRs/MRs for Corey to review and merge. Never commit or push directly to main, merge, or enable auto-merge on his behalf.
- Prefer one cohesive PR/MR and coordinated deployment per app when practical. Preserve required repository boundaries and safety/approval stages; link dependent PRs/MRs.
- For authorized changes, run relevant local/offline tests and checks before handoff, even while CI is disabled or paused. Report passed, failed and unrun checks. Offline validation never authorizes live changes.
