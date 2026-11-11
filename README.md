# perkforge-tenant-portal

The [Flux application entrypoint](gitops/README.md) keeps
app configuration tenant-owned while platform enrollment and security remain
outside this repository. Local is an enabled physical release candidate, not a deployed release. Independent
enrollment remains pinned to disabled v2.0.0 and suspended. Shared/dev defaults and
the historical Fleet path are unchanged.

## Configuration versions

See [RELEASING.md](RELEASING.md) for reviewed release PRs, immutable-tag
expectations, first-release ordering and the staged switch to tag-based refs.
