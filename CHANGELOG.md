# Changelog

## [3.8.0](https://github.com/steveyminecraft/ansible-role-regolith/compare/v3.7.1...v3.8.0) (2026-06-18)


### Features

* **ci:** gate integration and Galaxy on upstream test success ([b8ae562](https://github.com/steveyminecraft/ansible-role-regolith/commit/b8ae562e28aacdf75f5c4c22308d56f1d8e1d784))


### Bug Fixes

* **ci:** detect Release Please integration runs for AWS RC tests ([#35](https://github.com/steveyminecraft/ansible-role-regolith/issues/35)) ([d8ff66e](https://github.com/steveyminecraft/ansible-role-regolith/commit/d8ff66ebac452487420557de788fcfa6b2d9b2eb))
* **ci:** run AWS matrix jobs after prepare-matrix succeeds ([#37](https://github.com/steveyminecraft/ansible-role-regolith/issues/37)) ([645c9d6](https://github.com/steveyminecraft/ansible-role-regolith/commit/645c9d6eb44242cc07658ba6f5707f80fa57e0ac))
* **ci:** run integration on pull_request with prerequisite gate ([3bc8568](https://github.com/steveyminecraft/ansible-role-regolith/commit/3bc8568616496f80564fb268c7812be1ebb6d3a6))
* **ci:** trigger AWS RC tests via workflow_call on release PR ([#36](https://github.com/steveyminecraft/ansible-role-regolith/issues/36)) ([c2512b5](https://github.com/steveyminecraft/ansible-role-regolith/commit/c2512b5d9b0583e0ec11347d3f86b28bde8e5378))
* **ci:** unblock integration matrix after prerequisite gate ([0d311d0](https://github.com/steveyminecraft/ansible-role-regolith/commit/0d311d06adb62b93c56b7423e4b17cb929104909))

## [3.7.1](https://github.com/steveyminecraft/ansible-role-regolith/compare/v3.7.0...v3.7.1) (2026-06-18)


### Bug Fixes

* checkout repo before AWS prepare-matrix script runs ([612df67](https://github.com/steveyminecraft/ansible-role-regolith/commit/612df675854742038ce38cf7eb73c790a91bbb23))

## [3.7.0](https://github.com/steveyminecraft/ansible-role-regolith/compare/v3.6.0...v3.7.0) (2026-06-18)


### Features

* auto-run AWS RC tests from Release Please via workflow_call ([546c1c1](https://github.com/steveyminecraft/ansible-role-regolith/commit/546c1c13a6d13dab42a9b7d7fdd34ce6a03941b1))
* gate AWS RC tests on per-platform integration success ([6927ca9](https://github.com/steveyminecraft/ansible-role-regolith/commit/6927ca9194c594ede4aa731cbcc3c854c9fa2608))

## [3.6.0](https://github.com/steveyminecraft/ansible-role-regolith/compare/v3.5.3...v3.6.0) (2026-06-18)


### Features

* add testing pyramid and AWS remote harness ([01611d9](https://github.com/steveyminecraft/ansible-role-regolith/commit/01611d93048df796fe383152fdffdd3f0e3688b2))
* add testing pyramid and AWS remote harness ([f8c1e5c](https://github.com/steveyminecraft/ansible-role-regolith/commit/f8c1e5c9baf7f856799456582d8eec6a8cc312a3))


### Bug Fixes

* allow vagrant Molecule scenarios without dependency key ([4fe4f7d](https://github.com/steveyminecraft/ansible-role-regolith/commit/4fe4f7d6bc5ae733b1fe6c09a7e7d2fb2ba393cd))
* install ansible.posix for JSON stdout callback in CI ([c75ef6f](https://github.com/steveyminecraft/ansible-role-regolith/commit/c75ef6feb7886979b5a65e5bf632e87a43b05bca))
* restore GITHUB_TOKEN for Release Please after invalid PAT ([ba62d62](https://github.com/steveyminecraft/ansible-role-regolith/commit/ba62d62894c952f08a7cb12ddb2c23a6d53521aa))
* restore PLAY RECAP idempotence check in container integration tests ([7d18c57](https://github.com/steveyminecraft/ansible-role-regolith/commit/7d18c57b1f42e235c29d2894ee4b7c6991dd3297))
* satisfy ansible-lint and stabilize idempotence JSON parsing ([34f377b](https://github.com/steveyminecraft/ansible-role-regolith/commit/34f377bb9a03d0f24fe384214a1d02c5887040a7))
* use workspace path for idempotence JSON in container jobs ([074a26e](https://github.com/steveyminecraft/ansible-role-regolith/commit/074a26ea7fb25ce737d49928e3bb621f128f30b9))

## [3.5.3](https://github.com/steveyminecraft/ansible-role-regolith/compare/v3.5.2...v3.5.3) (2026-05-22)


### Bug Fixes

* avoid heredoc EOF failure in stable docs check ([#27](https://github.com/steveyminecraft/ansible-role-regolith/issues/27)) ([fb18293](https://github.com/steveyminecraft/ansible-role-regolith/commit/fb18293d50c374495755e4c743d4bdfd05b89a2a))

## [3.5.2](https://github.com/steveyminecraft/ansible-role-regolith/compare/v3.5.1...v3.5.2) (2026-05-22)


### Bug Fixes

* harden Galaxy release guardrails and clarify docs ([6324975](https://github.com/steveyminecraft/ansible-role-regolith/commit/6324975715e114de2c04cfa76f31ff0da31b14ed))
* harden Galaxy release guardrails and clarify docs ([63cd0c5](https://github.com/steveyminecraft/ansible-role-regolith/commit/63cd0c5059738e3bb81b04789152bbd5d51b238e))
* keep apt cache override internal to integration tests ([#17](https://github.com/steveyminecraft/ansible-role-regolith/issues/17)) ([824d630](https://github.com/steveyminecraft/ansible-role-regolith/commit/824d6300128064b27f4e6f2a2612a03632f01909))
* strictly validate Galaxy release tag input ([#16](https://github.com/steveyminecraft/ansible-role-regolith/issues/16)) ([e37ad82](https://github.com/steveyminecraft/ansible-role-regolith/commit/e37ad82a8d31b59531139b67704bc93967f27f0e))
* suite transition test assertions and skip apt for synthetic suite ([271afc5](https://github.com/steveyminecraft/ansible-role-regolith/commit/271afc558fc15e40a61d1846ebd69d415f17e66e))

## [3.5.1](https://github.com/steveyminecraft/ansible-role-regolith/compare/v3.5.0...v3.5.1) (2026-05-22)


### Bug Fixes

* converge repository configuration across supported setting changes ([d6812f1](https://github.com/steveyminecraft/ansible-role-regolith/commit/d6812f1a9f20c3c3b6693501dcfc0e09bb1765a3))
* converge repository configuration across supported setting changes ([4c22681](https://github.com/steveyminecraft/ansible-role-regolith/commit/4c2268103261d2daf740bf5d47159dc425f1bcf8))
* publish only versioned Regolith role tags to Galaxy ([ad94dee](https://github.com/steveyminecraft/ansible-role-regolith/commit/ad94deeaa08b5818efc2ec608aed9be2ffc0d95e))
* publish only versioned Regolith role tags to Galaxy ([a90e117](https://github.com/steveyminecraft/ansible-role-regolith/commit/a90e11713564c34b9197fba8c0eed11fcecbc407))
* reject mismatched repository architecture overrides ([cf9bb71](https://github.com/steveyminecraft/ansible-role-regolith/commit/cf9bb713eb1b7ce84fa6bb63132c890c861e4d4d))
* reject mismatched repository architecture overrides ([844356e](https://github.com/steveyminecraft/ansible-role-regolith/commit/844356e41fd75b84204e7e716ea66bef3cc1caab))
* restore Galaxy import composite action content ([871e5d8](https://github.com/steveyminecraft/ansible-role-regolith/commit/871e5d8c82dfe2e2fa8091ad0fc9344bca02ef65))

## [3.5.0](https://github.com/steveyminecraft/ansible-role-regolith/compare/v3.4.0...v3.5.0) (2026-05-22)


### Features

* complete regolith hardening plan ([c8f7560](https://github.com/steveyminecraft/ansible-role-regolith/commit/c8f75600f2c1282a326446cb6a66af1db3dc65b1))


### Bug Fixes

* reject unsupported regolith platforms ([d51fe99](https://github.com/steveyminecraft/ansible-role-regolith/commit/d51fe997139399ef0fce041dbcbb0b72bbf05269))
