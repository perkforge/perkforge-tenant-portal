# Household portal tenant deployment

This repository owns only namespaced portal application deployment configuration.
Read docs/architecture.md and docs/operations.md. Application source/image build is
in perkforge-portal. Platform owns namespace/project/quota, runtime service account,
RBAC, network policy, TLS ingress and Fleet registration. Keep enabled=false until
separate deployment approval. Never apply manifests, provision secrets/identity,
expand privileges, or enable paused services without authorization. No main pushes,
force pushes or merges. Never commit secrets, local evidence or fixture credentials.
