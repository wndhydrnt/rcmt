# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Any, Optional

from rcmt import source


class Context:
    def __init__(
        self, repo: source.Repository, custom_config: Optional[dict[str, Any]] = None
    ):
        self._custom_config = custom_config if custom_config is not None else {}
        self._tpl_data: dict[str, Any] = {
            "repo_name": repo.name,
            "repo_project": repo.project,
            "repo_source": repo.source,
        }
        self.repo = repo

    @property
    def custom_config(self) -> dict[str, Any]:
        return self._custom_config

    def get_template_data(self) -> dict[str, Any]:
        return self._tpl_data

    def set_template_key(self, key: str, value: Any):
        self._tpl_data[key] = value

    @property
    def template_data(self) -> dict[str, Any]:
        return self._tpl_data

    def update_template_data(self, d: dict[str, Any]):
        self._tpl_data.update(d)
