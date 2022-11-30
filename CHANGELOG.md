# Changelog

## [0.14.0](https://github.com/wndhydrnt/rcmt/compare/v0.13.0...v0.14.0) (2022-11-30)


### ⚠ BREAKING CHANGES

* Remove matchers `LineNotInFile` and `FileNotExists` ([#224](https://github.com/wndhydrnt/rcmt/issues/224))

### Features

* Add matchers `And` and `Not` ([#222](https://github.com/wndhydrnt/rcmt/issues/222)) ([0e09f24](https://github.com/wndhydrnt/rcmt/commit/0e09f2445a3f757ea660e69be0e3e8f8e3617e38))
* Remove matchers `LineNotInFile` and `FileNotExists` ([#224](https://github.com/wndhydrnt/rcmt/issues/224)) ([10448e9](https://github.com/wndhydrnt/rcmt/commit/10448e901843e470d9793730d6f4224b5768e577))
* Slugify branch names to ensure a branch gets created ([#225](https://github.com/wndhydrnt/rcmt/issues/225)) ([e4e2631](https://github.com/wndhydrnt/rcmt/commit/e4e26313d5a8384bf9a49a7a932477b40562f788))

## [0.13.0](https://github.com/wndhydrnt/rcmt/compare/v0.12.1...v0.13.0) (2022-11-27)


### Features

* Always delete base branch when closing a PR ([#219](https://github.com/wndhydrnt/rcmt/issues/219)) ([5e855ec](https://github.com/wndhydrnt/rcmt/commit/5e855ec5041e6d652d63033a914d142fc87a7ee2))
* Delete branch automatically after merge ([#184](https://github.com/wndhydrnt/rcmt/issues/184)) ([5bf0694](https://github.com/wndhydrnt/rcmt/commit/5bf0694a1c762d1a6dfa41b37bd3ad1e6e6f6aef))
* Improve help texts of command "local" and "run" ([#204](https://github.com/wndhydrnt/rcmt/issues/204)) ([f37f09d](https://github.com/wndhydrnt/rcmt/commit/f37f09d457fa0a51d6d9dcf369df949d07de62d7))
* Recreate a closed PR if `Run.merge_once` is `False` ([#220](https://github.com/wndhydrnt/rcmt/issues/220)) ([b64724e](https://github.com/wndhydrnt/rcmt/commit/b64724edca50f71bd15875fe55f523cd22c905d6))

## [0.12.1](https://github.com/wndhydrnt/rcmt/compare/v0.12.0...v0.12.1) (2022-08-18)


### Bug Fixes

* GitLab MR gets merged even though it has not been approved ([#179](https://github.com/wndhydrnt/rcmt/issues/179)) ([83c715f](https://github.com/wndhydrnt/rcmt/commit/83c715f91bc97da3825b6eeccc2ae3b0d5c0ca42))

## [0.12.0](https://github.com/wndhydrnt/rcmt/compare/v0.11.2...v0.12.0) (2022-08-12)


### Features

* Check approvals before merging GitLab MR ([#176](https://github.com/wndhydrnt/rcmt/issues/176)) ([b15be8f](https://github.com/wndhydrnt/rcmt/commit/b15be8f801888cb599a66b5fb0d2a1548cfb8849))


### Bug Fixes

* auto_merge_after fails on GitLab ([#178](https://github.com/wndhydrnt/rcmt/issues/178)) ([9e03e39](https://github.com/wndhydrnt/rcmt/commit/9e03e393d6311772e77f2f0da38b1e08649d19a3))

## [0.11.2](https://github.com/wndhydrnt/rcmt/compare/v0.11.1...v0.11.2) (2022-07-27)


### Bug Fixes

* Remove invalid parameter of Run.add_matcher() ([12d3c31](https://github.com/wndhydrnt/rcmt/commit/12d3c31cb0aa6d45833095663fc17f876b68f92b))

## [0.11.1](https://github.com/wndhydrnt/rcmt/compare/v0.11.0...v0.11.1) (2022-07-27)


### Bug Fixes

* Run fails if a repository is empty ([#155](https://github.com/wndhydrnt/rcmt/issues/155)) ([351e10d](https://github.com/wndhydrnt/rcmt/commit/351e10d2849c2be1835efd4ed6b99e5ae19d327f))

## [0.11.0](https://github.com/wndhydrnt/rcmt/compare/v0.10.0...v0.11.0) (2022-07-26)


### ⚠ BREAKING CHANGES

* Remove "rcmt.package" module (#145)

### Features

* Add matchers FileNotExists and LineNotInFile ([#143](https://github.com/wndhydrnt/rcmt/issues/143)) ([6624c46](https://github.com/wndhydrnt/rcmt/commit/6624c46966f6d5a8a6200ec39f44e0b463f542db))
* Remove "rcmt.package" module ([#145](https://github.com/wndhydrnt/rcmt/issues/145)) ([9c190a3](https://github.com/wndhydrnt/rcmt/commit/9c190a3ac8eaaa641bcaf75cf4649ff34664b32c))


### Bug Fixes

* Exception thrown by a Matcher breaks a Run ([#149](https://github.com/wndhydrnt/rcmt/issues/149)) ([14ef32a](https://github.com/wndhydrnt/rcmt/commit/14ef32ae358cb876f0f9f4d19a35a01a14eeb417))
* Run throws exception if branch has no changes and no PR is open ([#153](https://github.com/wndhydrnt/rcmt/issues/153)) ([0f0503d](https://github.com/wndhydrnt/rcmt/commit/0f0503d08b41aa01d94fb4c0ecff5a55bc790411))

## [0.10.0](https://github.com/wndhydrnt/rcmt/compare/v0.9.0...v0.10.0) (2022-07-17)


### Features

* Add message about ignoring PRs only if merge_once is set ([#140](https://github.com/wndhydrnt/rcmt/issues/140)) ([66cda39](https://github.com/wndhydrnt/rcmt/commit/66cda390e3d8306fc81edd015fb016e64a4db47e))
* Close pull request if changes are already present in base branch ([#135](https://github.com/wndhydrnt/rcmt/issues/135)) ([e6b5eb8](https://github.com/wndhydrnt/rcmt/commit/e6b5eb86281c4c7e12f51ef5cf2d8eb7d0c234d6))
* Detail configuration of Run in body of PR ([#139](https://github.com/wndhydrnt/rcmt/issues/139)) ([98c5e3a](https://github.com/wndhydrnt/rcmt/commit/98c5e3a64b9dc27a6f6e3f46b7a975f9cc74d336))
* Update title or body of PR if they change ([#141](https://github.com/wndhydrnt/rcmt/issues/141)) ([61ca43b](https://github.com/wndhydrnt/rcmt/commit/61ca43b1bc696e17ca96b9534e7e2bf269631643))

## [0.9.0](https://github.com/wndhydrnt/rcmt/compare/v0.8.2...v0.9.0) (2022-07-07)


### Features

* Add matcher "Or" ([#133](https://github.com/wndhydrnt/rcmt/issues/133)) ([0cbf59e](https://github.com/wndhydrnt/rcmt/commit/0cbf59e6927923d15cebf0bb28de0cf73d8acdc9))
* Supply more than one run file to the "run" command ([#128](https://github.com/wndhydrnt/rcmt/issues/128)) ([c3f01dc](https://github.com/wndhydrnt/rcmt/commit/c3f01dc301cfd50cff9c6100a6b87b378b6d07dd))


### Bug Fixes

* Action "Absent" does not delete directories ([#134](https://github.com/wndhydrnt/rcmt/issues/134)) ([d7ea762](https://github.com/wndhydrnt/rcmt/commit/d7ea762eb13c692996dd8ef8a0492141aa04371b))

## [0.8.2](https://github.com/wndhydrnt/rcmt/compare/v0.8.1...v0.8.2) (2022-06-27)


### Bug Fixes

* **docs:** Fix readthedocs failing to build documentation ([#125](https://github.com/wndhydrnt/rcmt/issues/125)) ([e758f37](https://github.com/wndhydrnt/rcmt/commit/e758f37eaeae026a0253bdde872273e63b858126))
* rcmt does not work with every poetry project due to version constraint ([#123](https://github.com/wndhydrnt/rcmt/issues/123)) ([648e66b](https://github.com/wndhydrnt/rcmt/commit/648e66b9246d39e39d238b7ae184a34133bb6df2))

## [0.8.1](https://github.com/wndhydrnt/rcmt/compare/v0.8.0...v0.8.1) (2022-06-23)


### Bug Fixes

* Release 0.8.1 ([f8868b4](https://github.com/wndhydrnt/rcmt/commit/f8868b4d1c85bbc57465928d928e163c882cb1ea))

## [0.8.0](https://github.com/wndhydrnt/rcmt/compare/v0.7.0...v0.8.0) (2022-06-23)


### ⚠ BREAKING CHANGES

* Move module "action" under module "rcmt" (#121)

### Features

* Add matcher LineInFile ([#120](https://github.com/wndhydrnt/rcmt/issues/120)) ([2953f5c](https://github.com/wndhydrnt/rcmt/commit/2953f5c4a3778833fb852a9780ba0858b695cb0f))
* Move module "action" under module "rcmt" ([#121](https://github.com/wndhydrnt/rcmt/issues/121)) ([1d12c1b](https://github.com/wndhydrnt/rcmt/commit/1d12c1b34c4d8ba099c1cd411e02b0c9651e2fc2))
* Support Python 3.10 ([#118](https://github.com/wndhydrnt/rcmt/issues/118)) ([5b5f1b8](https://github.com/wndhydrnt/rcmt/commit/5b5f1b8068ea78c74b845af475a198a7e8dcb90c))


### Miscellaneous Chores

* release 0.8.0 ([5ce594d](https://github.com/wndhydrnt/rcmt/commit/5ce594d9b03d12e827da77b84d7dfe4bab81a5bc))
