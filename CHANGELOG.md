# Changelog

## [0.27.2](https://github.com/wndhydrnt/rcmt/compare/v0.27.1...v0.27.2) (2023-11-15)


### Bug Fixes

* **verify:** apply task in checkout directory ([#458](https://github.com/wndhydrnt/rcmt/issues/458)) ([1591d1f](https://github.com/wndhydrnt/rcmt/commit/1591d1f6c27f8987ac5d0cad434d67b0bceeb3d1))

## [0.27.1](https://github.com/wndhydrnt/rcmt/compare/v0.27.0...v0.27.1) (2023-11-14)


### Bug Fixes

* **deps:** update dependency sqlalchemy to v2.0.23 ([#453](https://github.com/wndhydrnt/rcmt/issues/453)) ([c7a7297](https://github.com/wndhydrnt/rcmt/commit/c7a7297ecfbc785932dd418ad170c771af4f6c9a))
* **git:** set branch name when rebasing from remote ([#455](https://github.com/wndhydrnt/rcmt/issues/455)) ([8d03967](https://github.com/wndhydrnt/rcmt/commit/8d03967aec0845caf9b9fd4e82614c2d03c78d26))

## [0.27.0](https://github.com/wndhydrnt/rcmt/compare/v0.26.0...v0.27.0) (2023-11-07)


### ⚠ BREAKING CHANGES

* Define Task as a class ([#440](https://github.com/wndhydrnt/rcmt/issues/440))

### Features

* Define Task as a class ([#440](https://github.com/wndhydrnt/rcmt/issues/440)) ([74b572c](https://github.com/wndhydrnt/rcmt/commit/74b572c25a351f4e4538acb03a1c32487f284861))
* **docs:** Add tutorial that describes how to bootstrap a project ([#451](https://github.com/wndhydrnt/rcmt/issues/451)) ([e8c29e2](https://github.com/wndhydrnt/rcmt/commit/e8c29e2f6bcf1fdced7c1480065d94f5eda4ec16))
* raise an error if a Task has been defined but not registered ([#444](https://github.com/wndhydrnt/rcmt/issues/444)) ([12ca68f](https://github.com/wndhydrnt/rcmt/commit/12ca68f8c178f29581112b76bb4e4ff95c8fa2f1))
* **unittest:** create helper class for writing unit tests ([#452](https://github.com/wndhydrnt/rcmt/issues/452)) ([f700a21](https://github.com/wndhydrnt/rcmt/commit/f700a21882a602e9f5f6a69871ea0ab409b52e65))


### Bug Fixes

* **deps:** update dependency alembic to v1.12.1 ([#448](https://github.com/wndhydrnt/rcmt/issues/448)) ([33dedbc](https://github.com/wndhydrnt/rcmt/commit/33dedbc2eeb9bd618c724c07ee7cbfdb1b8882ea))
* **deps:** update dependency greenlet to v3.0.1 ([#447](https://github.com/wndhydrnt/rcmt/issues/447)) ([fb81e47](https://github.com/wndhydrnt/rcmt/commit/fb81e47e49a81397ce40ac73b2a03d009aca929a))
* validate command does not work with class-based Task definitions ([#443](https://github.com/wndhydrnt/rcmt/issues/443)) ([0e93efd](https://github.com/wndhydrnt/rcmt/commit/0e93efd17c7740fdb34cf3637ff461d5c48ac23b))

## [0.26.0](https://github.com/wndhydrnt/rcmt/compare/v0.25.0...v0.26.0) (2023-10-27)


### Features

* add event handling for pull requests ([#428](https://github.com/wndhydrnt/rcmt/issues/428)) ([2458997](https://github.com/wndhydrnt/rcmt/commit/245899749341e94efe4f1e6ce516aaa495ace757))
* pass custom configuration to filters and event handlers ([#435](https://github.com/wndhydrnt/rcmt/issues/435)) ([d040304](https://github.com/wndhydrnt/rcmt/commit/d0403046c05b19ce393fdc27da0bbfe5194147a9))
* prevent overriding commits in a branch that were not made by rcmt ([#439](https://github.com/wndhydrnt/rcmt/issues/439)) ([215b44f](https://github.com/wndhydrnt/rcmt/commit/215b44ff8b4988403bb417b9c7c00f85b22d70d7))


### Bug Fixes

* **deps:** update dependency gitpython to v3.1.38 ([#436](https://github.com/wndhydrnt/rcmt/issues/436)) ([832ba22](https://github.com/wndhydrnt/rcmt/commit/832ba22c388ac9eb6b56a9f4b07a5286fc221d21))
* **deps:** update dependency sqlalchemy to v2.0.22 ([#433](https://github.com/wndhydrnt/rcmt/issues/433)) ([a53a5ff](https://github.com/wndhydrnt/rcmt/commit/a53a5ff73486e6ad45bffc1a0118e1dca3ae735f))
* **deps:** update dependency structlog to &gt;=23.2,&lt;23.3 ([#427](https://github.com/wndhydrnt/rcmt/issues/427)) ([800c79c](https://github.com/wndhydrnt/rcmt/commit/800c79c42e6feace7ec86d8e6c9dcfc2d9c1d26a))
* fix mypy not validating task files ([#430](https://github.com/wndhydrnt/rcmt/issues/430)) ([4913e2f](https://github.com/wndhydrnt/rcmt/commit/4913e2faee7237032aa3dda1d8e1d1b429629b09))

## [0.25.0](https://github.com/wndhydrnt/rcmt/compare/v0.24.0...v0.25.0) (2023-10-15)


### Features

* create module "filter" and deprecate module "matcher" ([#425](https://github.com/wndhydrnt/rcmt/issues/425)) ([f315185](https://github.com/wndhydrnt/rcmt/commit/f315185ea4dab811d19592fed621f6f8570734b8))
* remove experimental semgrep support ([#421](https://github.com/wndhydrnt/rcmt/issues/421)) ([cd80a67](https://github.com/wndhydrnt/rcmt/commit/cd80a67dee1ddf3272bc1c147038d59754d60124))
* Switch license to MPL 2.0 ([#423](https://github.com/wndhydrnt/rcmt/issues/423)) ([9cd03d9](https://github.com/wndhydrnt/rcmt/commit/9cd03d94405829ec05aa41c45b8ecea82fed747d))

## [0.24.0](https://github.com/wndhydrnt/rcmt/compare/v0.23.2...v0.24.0) (2023-10-11)


### ⚠ BREAKING CHANGES

* Templating with Jinja ([#419](https://github.com/wndhydrnt/rcmt/issues/419))

### Features

* add support for Python 3.12 ([#412](https://github.com/wndhydrnt/rcmt/issues/412)) ([8ab05f4](https://github.com/wndhydrnt/rcmt/commit/8ab05f481359a37acb55d3e09030b8137aca7824))
* define labels of pull request via a Task ([#415](https://github.com/wndhydrnt/rcmt/issues/415)) ([3f793cf](https://github.com/wndhydrnt/rcmt/commit/3f793cf351e842e437abfb825c58ff8cc59e973e))
* Templating with Jinja ([#419](https://github.com/wndhydrnt/rcmt/issues/419)) ([64e60c8](https://github.com/wndhydrnt/rcmt/commit/64e60c8315d5e40469135df28907573d827dfc70))


### Bug Fixes

* **deps:** update dependency semgrep to v1.42.0 ([#414](https://github.com/wndhydrnt/rcmt/issues/414)) ([fcc993a](https://github.com/wndhydrnt/rcmt/commit/fcc993a3a1a527cb2d6918b996b9ea040c04988f))


### Miscellaneous Chores

* release 0.24.0 ([946a9f1](https://github.com/wndhydrnt/rcmt/commit/946a9f112fd6937384adb70dbe9536e5d46984a4))

## [0.23.2](https://github.com/wndhydrnt/rcmt/compare/v0.23.1...v0.23.2) (2023-10-03)


### Bug Fixes

* **deps:** update dependency gitpython to v3.1.36 ([#400](https://github.com/wndhydrnt/rcmt/issues/400)) ([c0a5f39](https://github.com/wndhydrnt/rcmt/commit/c0a5f397f83b73c1aff3a09d329a0304815f3d4f))
* **deps:** update dependency gitpython to v3.1.37 ([#407](https://github.com/wndhydrnt/rcmt/issues/407)) ([61dceaf](https://github.com/wndhydrnt/rcmt/commit/61dceafd07ac40f8993bf230e9b25ad6446d2394))
* **deps:** update dependency pydantic to v2.4.0 ([#409](https://github.com/wndhydrnt/rcmt/issues/409)) ([0ae8794](https://github.com/wndhydrnt/rcmt/commit/0ae879466fcafea9fe9e5a34b47e93a1e1bc6870))
* **deps:** update dependency semgrep to v1.40.0 ([#402](https://github.com/wndhydrnt/rcmt/issues/402)) ([523f8ce](https://github.com/wndhydrnt/rcmt/commit/523f8ceb08ad63bb68b21961202c93773b1a4759))
* **deps:** update dependency sqlalchemy to v2.0.21 ([#404](https://github.com/wndhydrnt/rcmt/issues/404)) ([e64a4b1](https://github.com/wndhydrnt/rcmt/commit/e64a4b107ee7143091dc52f4b388f92741307c1e))
* **git:** do not fail when default branch has been renamed ([#410](https://github.com/wndhydrnt/rcmt/issues/410)) ([fbbf112](https://github.com/wndhydrnt/rcmt/commit/fbbf11267fcf8c794614fea9510ca9252d66865c))
* **git:** handle generic git command errors ([#411](https://github.com/wndhydrnt/rcmt/issues/411)) ([c051661](https://github.com/wndhydrnt/rcmt/commit/c0516610cae51b9b2ed6f215b35f3395c6b3fd5c))


### Documentation

* Port documentation to mkdocs ([#405](https://github.com/wndhydrnt/rcmt/issues/405)) ([7b93aa5](https://github.com/wndhydrnt/rcmt/commit/7b93aa5bf2c6fade64842313ed4394479e381173))

## [0.23.1](https://github.com/wndhydrnt/rcmt/compare/v0.23.0...v0.23.1) (2023-09-13)


### Bug Fixes

* **docs:** empty pages after upgrade of sphinx ([#396](https://github.com/wndhydrnt/rcmt/issues/396)) ([4434097](https://github.com/wndhydrnt/rcmt/commit/443409739e4f97971e8edb25552beaf12746e730))

## [0.23.0](https://github.com/wndhydrnt/rcmt/compare/v0.22.0...v0.23.0) (2023-09-12)


### Features

* **action:** add experimental support for semgrep ([#389](https://github.com/wndhydrnt/rcmt/issues/389)) ([d1f3308](https://github.com/wndhydrnt/rcmt/commit/d1f33085c027e4706e1a697d7a013ad9823b0451))
* **action:** let exec action pass arguments to executable ([#390](https://github.com/wndhydrnt/rcmt/issues/390)) ([8450d02](https://github.com/wndhydrnt/rcmt/commit/8450d02f04e68c3f572eacf9ceeb128285a064bd))


### Bug Fixes

* **deps:** update dependency alembic to v1.12.0 ([#384](https://github.com/wndhydrnt/rcmt/issues/384)) ([aae4eeb](https://github.com/wndhydrnt/rcmt/commit/aae4eebee059a33b56adace41be26f9e956d8b27))
* **deps:** update dependency gitpython to v3.1.33 ([#385](https://github.com/wndhydrnt/rcmt/issues/385)) ([41ed4d4](https://github.com/wndhydrnt/rcmt/commit/41ed4d421720cc7603b882ee47dcfb334cf0b3f1))
* **deps:** update dependency pydantic to v2 ([#378](https://github.com/wndhydrnt/rcmt/issues/378)) ([a46a0f3](https://github.com/wndhydrnt/rcmt/commit/a46a0f331e3972390f7f8967d7ecc8157c06355c))
* **deps:** update dependency pydantic to v2.3.0 ([#381](https://github.com/wndhydrnt/rcmt/issues/381)) ([137b155](https://github.com/wndhydrnt/rcmt/commit/137b155fbe3a0e25ba7e48b6397e3df528f5eab1))
* **deps:** update dependency pygithub to v1.59.1 ([#364](https://github.com/wndhydrnt/rcmt/issues/364)) ([adb15f8](https://github.com/wndhydrnt/rcmt/commit/adb15f854ff17382652ef8255ec3c7267fbd6288))
* **deps:** update dependency python-gitlab to v3.15.0 ([#365](https://github.com/wndhydrnt/rcmt/issues/365)) ([76513f3](https://github.com/wndhydrnt/rcmt/commit/76513f3507ce77155257c103704f41f05f7d8565))
* **deps:** update dependency structlog to v23 ([#373](https://github.com/wndhydrnt/rcmt/issues/373)) ([31836ec](https://github.com/wndhydrnt/rcmt/commit/31836eccf17f35211c18be6dc65b8c24f9201e82))
* **git:** changes in branch not always removed ([#394](https://github.com/wndhydrnt/rcmt/issues/394)) ([d744c4c](https://github.com/wndhydrnt/rcmt/commit/d744c4c7470fc6dfbfd0017726fcaaef22cd9c04))

## [0.22.0](https://github.com/wndhydrnt/rcmt/compare/v0.21.1...v0.22.0) (2023-08-21)


### Features

* Declare multiple Tasks in one file ([#343](https://github.com/wndhydrnt/rcmt/issues/343)) ([cf31aad](https://github.com/wndhydrnt/rcmt/commit/cf31aad62e2a0eb766582df020e11c43554cba3e))


### Bug Fixes

* **deps:** update dependency alembic to v1.11.2 ([#352](https://github.com/wndhydrnt/rcmt/issues/352)) ([3da4ba9](https://github.com/wndhydrnt/rcmt/commit/3da4ba961b58ffffed915674f8211a6e9fa915ad))
* **deps:** update dependency click to v8.1.6 ([#353](https://github.com/wndhydrnt/rcmt/issues/353)) ([4848d94](https://github.com/wndhydrnt/rcmt/commit/4848d945b92c7acb6c8ccae9ac93e370449a78df))
* **deps:** update dependency humanize to v4.7.0 ([#363](https://github.com/wndhydrnt/rcmt/issues/363)) ([d3eb887](https://github.com/wndhydrnt/rcmt/commit/d3eb887efbb3bee6fa7bd6956bfde2d7765a97b1))
* **deps:** update dependency pydantic to v1.10.12 ([#354](https://github.com/wndhydrnt/rcmt/issues/354)) ([c80ec84](https://github.com/wndhydrnt/rcmt/commit/c80ec8445ecd3cd5c5d540074a32efbae548a2b6))
* **deps:** update dependency python-slugify to v8.0.1 ([#355](https://github.com/wndhydrnt/rcmt/issues/355)) ([7a01918](https://github.com/wndhydrnt/rcmt/commit/7a01918be50918d55f44470e3c40646f4be1260a))
* **deps:** update dependency pyyaml to v6.0.1 ([#357](https://github.com/wndhydrnt/rcmt/issues/357)) ([c267a6b](https://github.com/wndhydrnt/rcmt/commit/c267a6bcfe4adc6c0f1f430f138bacb417f94289))
* **deps:** update dependency sqlalchemy to v2.0.19 ([#358](https://github.com/wndhydrnt/rcmt/issues/358)) ([73f03ff](https://github.com/wndhydrnt/rcmt/commit/73f03ff5a903c9d6f6a2efd875ac9a342c79fd3c))
* **gitlab:** ignore archived project when listing open merge requests ([#375](https://github.com/wndhydrnt/rcmt/issues/375)) ([a124968](https://github.com/wndhydrnt/rcmt/commit/a12496892bcfb600501bfb9146ce483d4719a4ef))

## [0.21.1](https://github.com/wndhydrnt/rcmt/compare/v0.21.0...v0.21.1) (2023-08-15)


### Bug Fixes

* Same change gets pushed multiple times ([#344](https://github.com/wndhydrnt/rcmt/issues/344)) ([e53a1c1](https://github.com/wndhydrnt/rcmt/commit/e53a1c1fa95237ff01059b4753bf071e39ff029a))

## [0.21.0](https://github.com/wndhydrnt/rcmt/compare/v0.20.1...v0.21.0) (2023-08-09)


### Features

* Add argument "repository" to command "run" ([#333](https://github.com/wndhydrnt/rcmt/issues/333)) ([608bf53](https://github.com/wndhydrnt/rcmt/commit/608bf53a8458ed76846254788782707f25fe02bd))
* Let Task accept callables as Actions and Matchers ([#335](https://github.com/wndhydrnt/rcmt/issues/335)) ([f400793](https://github.com/wndhydrnt/rcmt/commit/f400793fb6198a98892baf65b2bf419a206482ff))


### Bug Fixes

* Continue execution if Task causes exception ([#339](https://github.com/wndhydrnt/rcmt/issues/339)) ([bf2de85](https://github.com/wndhydrnt/rcmt/commit/bf2de85dbcbf4c26bb85d9dad1f1422551973a64))

## [0.20.1](https://github.com/wndhydrnt/rcmt/compare/v0.20.0...v0.20.1) (2023-06-26)


### Bug Fixes

* FileExists Matcher with nested search does not work for GitLab repositories ([#329](https://github.com/wndhydrnt/rcmt/issues/329)) ([975cd04](https://github.com/wndhydrnt/rcmt/commit/975cd04912fd8d5c9d58814f83f79d29ae49e009))

## [0.20.0](https://github.com/wndhydrnt/rcmt/compare/v0.19.1...v0.20.0) (2023-06-22)


### Features

* Add command "validate" ([#326](https://github.com/wndhydrnt/rcmt/issues/326)) ([a59238d](https://github.com/wndhydrnt/rcmt/commit/a59238d4b23efa8f5cb14dbeb77add2a86d6eb30))
* Add property "full_name" to source.Repository ([#327](https://github.com/wndhydrnt/rcmt/issues/327)) ([84f41c3](https://github.com/wndhydrnt/rcmt/commit/84f41c3923562171bf8e3e7838fe6af6c2ef6aba))
* Default representation of Matcher classes ([#328](https://github.com/wndhydrnt/rcmt/issues/328)) ([560896d](https://github.com/wndhydrnt/rcmt/commit/560896d5c54ec4ced75d0b8c2af693b85e30bb11))
* Support writing logs as JSON ([#324](https://github.com/wndhydrnt/rcmt/issues/324)) ([cdf89de](https://github.com/wndhydrnt/rcmt/commit/cdf89de11761575965321308849dd0ddd7d8d89a))

## [0.19.1](https://github.com/wndhydrnt/rcmt/compare/v0.19.0...v0.19.1) (2023-06-16)


### Bug Fixes

* Fix wrong git command to validate branch name ([#322](https://github.com/wndhydrnt/rcmt/issues/322)) ([fadacfe](https://github.com/wndhydrnt/rcmt/commit/fadacfeecd2a2fd7052b61267997500f9201d7af))

## [0.19.0](https://github.com/wndhydrnt/rcmt/compare/v0.18.0...v0.19.0) (2023-06-15)


### ⚠ BREAKING CHANGES

* Do not slugify custom branch names ([#321](https://github.com/wndhydrnt/rcmt/issues/321))
* Replace command "local" with "verify" ([#319](https://github.com/wndhydrnt/rcmt/issues/319))

### Features

* Replace command "local" with "verify" ([#319](https://github.com/wndhydrnt/rcmt/issues/319)) ([3ab7f87](https://github.com/wndhydrnt/rcmt/commit/3ab7f87457c895489dd8257ddcd6543fabafed3d))


### Bug Fixes

* Do not slugify custom branch names ([#321](https://github.com/wndhydrnt/rcmt/issues/321)) ([8e0ebe0](https://github.com/wndhydrnt/rcmt/commit/8e0ebe0119148759ebaf2128bd4c9f301b8734ec))

## [0.18.0](https://github.com/wndhydrnt/rcmt/compare/v0.17.1...v0.18.0) (2023-06-07)


### Features

* Raise an exception if no sources have been configured ([#314](https://github.com/wndhydrnt/rcmt/issues/314)) ([a2b5340](https://github.com/wndhydrnt/rcmt/commit/a2b5340ce73419be1bb125b59d39fe58eadb83f9))


### Bug Fixes

* Fix RuntimeError when passing relative path to "rcmt local" ([#313](https://github.com/wndhydrnt/rcmt/issues/313)) ([0d863a0](https://github.com/wndhydrnt/rcmt/commit/0d863a06f9ca4554b1a1ee4a220327fd40f89571))

## [0.17.1](https://github.com/wndhydrnt/rcmt/compare/v0.17.0...v0.17.1) (2023-04-20)


### Bug Fixes

* git pull can fail if repository names overlap ([#300](https://github.com/wndhydrnt/rcmt/issues/300)) ([f33947f](https://github.com/wndhydrnt/rcmt/commit/f33947fb599d56257f84cb5b5e0b9d4ce88e1369))

## [0.17.0](https://github.com/wndhydrnt/rcmt/compare/v0.16.0...v0.17.0) (2023-03-28)


### Features

* Add setting to limit the number of changes per run of Task ([#290](https://github.com/wndhydrnt/rcmt/issues/290)) ([09f23a2](https://github.com/wndhydrnt/rcmt/commit/09f23a228059838a611e6fb55beb31e5381e146d))

## [0.16.0](https://github.com/wndhydrnt/rcmt/compare/v0.15.3...v0.16.0) (2023-03-05)


### Features

* Add flag "enabled" to "Run" ([#276](https://github.com/wndhydrnt/rcmt/issues/276)) ([20363f9](https://github.com/wndhydrnt/rcmt/commit/20363f98319ad44992f0f9e6665a20ef846aae3e))
* Rename "Run" to "Task" ([#288](https://github.com/wndhydrnt/rcmt/issues/288)) ([878f80d](https://github.com/wndhydrnt/rcmt/commit/878f80d441e9959ee090d6d563accc425efdcac5))

## [0.15.3](https://github.com/wndhydrnt/rcmt/compare/v0.15.2...v0.15.3) (2023-01-18)


### Bug Fixes

* Change of one run leaks into another if they both target the same repository ([#259](https://github.com/wndhydrnt/rcmt/issues/259)) ([e773de2](https://github.com/wndhydrnt/rcmt/commit/e773de203e06e05ca55322d459ff9b57001d5e5d))

## [0.15.2](https://github.com/wndhydrnt/rcmt/compare/v0.15.1...v0.15.2) (2023-01-16)


### Bug Fixes

* Merge test causes exception due to missing user configuration ([#255](https://github.com/wndhydrnt/rcmt/issues/255)) ([b1690df](https://github.com/wndhydrnt/rcmt/commit/b1690df8ce986c8856a43abfd24009e411689616))

## [0.15.1](https://github.com/wndhydrnt/rcmt/compare/v0.15.0...v0.15.1) (2023-01-15)


### Bug Fixes

* Empty Pull Request created after merging a previous Pull Request ([#251](https://github.com/wndhydrnt/rcmt/issues/251)) ([b4bd1fe](https://github.com/wndhydrnt/rcmt/commit/b4bd1fe4cb78991a987ce792b889f3ab8cb2849f))

## [0.15.0](https://github.com/wndhydrnt/rcmt/compare/v0.14.0...v0.15.0) (2023-01-11)


### Features

* Reduce number of processed repositories per Run ([#232](https://github.com/wndhydrnt/rcmt/issues/232)) ([0ef0582](https://github.com/wndhydrnt/rcmt/commit/0ef0582a5ba08bd218273f0cb6a950cd536a1d84))


### Bug Fixes

* Add line breaks to actions in pull request body on GitLab ([#243](https://github.com/wndhydrnt/rcmt/issues/243)) ([4f37ea9](https://github.com/wndhydrnt/rcmt/commit/4f37ea97a9e4ed6f2e6f5ae4fa68b4918befbb64))
* Let rcmt resolve a merge conflict automatically ([#245](https://github.com/wndhydrnt/rcmt/issues/245)) ([734bb7b](https://github.com/wndhydrnt/rcmt/commit/734bb7b4bc9013ad5d6829ddb07da101d5f07989))

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
