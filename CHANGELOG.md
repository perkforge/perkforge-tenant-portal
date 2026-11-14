# Changelog

## [2.3.0](https://github.com/perkforge/perkforge-tenant-portal/compare/v2.2.0...v2.3.0) (2026-11-14)


### Features

* deliver verified enrollment inventory through GitOps ConfigMap ([#23](https://github.com/perkforge/perkforge-tenant-portal/issues/23)) ([942ca93](https://github.com/perkforge/perkforge-tenant-portal/commit/942ca93b701a87ffcb44279f04f1c2cd2539cef3))
* select published Portal inventory reader and source baseline ([#25](https://github.com/perkforge/perkforge-tenant-portal/issues/25)) ([22be777](https://github.com/perkforge/perkforge-tenant-portal/commit/22be7775e8df9fb22737f33f9fcc655c86fd0f6a))

## [2.2.0](https://github.com/perkforge/perkforge-tenant-portal/compare/v2.1.1...v2.2.0) (2026-11-14)


### Features

* pin Portal LikeC4 identity document release ([#21](https://github.com/perkforge/perkforge-tenant-portal/issues/21)) ([1df91fb](https://github.com/perkforge/perkforge-tenant-portal/commit/1df91fbfc43d4f857f3c6ec161b246130c51cc73))

## [2.1.1](https://github.com/perkforge/perkforge-tenant-portal/compare/v2.1.0...v2.1.1) (2026-11-14)


### Bug Fixes

* **portal:** pin independent platform admin image ([#19](https://github.com/perkforge/perkforge-tenant-portal/issues/19)) ([6873057](https://github.com/perkforge/perkforge-tenant-portal/commit/68730576a6e9ec021c7a0dda0c743f7c5e6a93a8))

## [2.1.0](https://github.com/perkforge/perkforge-tenant-portal/compare/v2.0.0...v2.1.0) (2026-11-11)


### Features

* prepare physical Portal app activation ([#17](https://github.com/perkforge/perkforge-tenant-portal/issues/17)) ([f4bf6e1](https://github.com/perkforge/perkforge-tenant-portal/commit/f4bf6e1a75781372bde8253bd2249285bf626138))

## [2.0.0](https://github.com/perkforge/perkforge-tenant-portal/compare/v1.0.0...v2.0.0) (2026-11-10)


### ⚠ BREAKING CHANGES

* **gitops:** local now targets the physical platform with new origin, issuer and worker placement, and is disabled/suspended. Enrollment and platform consumers require coordinated compatible releases and separate activation approval.

### Bug Fixes

* **gitops:** prepare paused physical Portal configuration ([#15](https://github.com/perkforge/perkforge-tenant-portal/issues/15)) ([a10def7](https://github.com/perkforge/perkforge-tenant-portal/commit/a10def7fcb13589853d46162fdf6bddbb7f5a4cb))

## [1.0.0](https://github.com/perkforge/perkforge-tenant-portal/compare/v0.3.0...v1.0.0) (2026-10-31)


### ⚠ BREAKING CHANGES

* **gitops:** cluster, environment and profile annotations now use platform.perkforge.io instead of the former illustrative namespace. Enrollment consumers require a compatible release before advancing their pin.

### Bug Fixes

* **gitops:** migrate selection annotations to platform namespace ([#12](https://github.com/perkforge/perkforge-tenant-portal/issues/12)) ([d3e72ff](https://github.com/perkforge/perkforge-tenant-portal/commit/d3e72ff9301466bbb16ac7d0e4130f5340a6e010))

## [0.3.0](https://github.com/perkforge/perkforge-tenant-portal/compare/v0.2.0...v0.3.0) (2026-10-29)


### Features

* **portal:** select local activation explicitly ([#10](https://github.com/perkforge/perkforge-tenant-portal/issues/10)) ([a5d3a6f](https://github.com/perkforge/perkforge-tenant-portal/commit/a5d3a6f544d5de7f7927ddbb3c0cd97e611fcda9))

## [0.2.0](https://github.com/perkforge/perkforge-tenant-portal/compare/v0.1.0...v0.2.0) (2026-10-29)


### Features

* **portal:** prepare admin-only local Flux deployment ([#8](https://github.com/perkforge/perkforge-tenant-portal/issues/8)) ([6d51a27](https://github.com/perkforge/perkforge-tenant-portal/commit/6d51a27a9b0b00c7dee87cb980fe28a9f09ccbaa))

## 0.1.0 (2026-10-28)


### Features

* **release:** add reviewed configuration version tags ([#6](https://github.com/perkforge/perkforge-tenant-portal/issues/6)) ([17b23ec](https://github.com/perkforge/perkforge-tenant-portal/commit/17b23ec88f38f1949332fe9595493faf17706fb9))
