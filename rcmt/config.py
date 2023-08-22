import os.path
import tempfile
from typing import Any, Optional

import pydantic
import yaml
from pydantic.fields import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class Database(pydantic.BaseModel):
    connection: str = "sqlite:///:memory:"
    migrate: bool = True


class Git(pydantic.BaseModel):
    branch_prefix: str = "rcmt/"
    clone_options: dict[str, Any] = {"filter": "blob:none"}
    data_dir: str = os.path.join(tempfile.gettempdir(), "rcmt", "data")
    user_name: str = "rcmt"
    user_email: str = ""


class Github(pydantic.BaseModel):
    access_token: str = ""
    base_url: str = "https://api.github.com"


class Gitlab(pydantic.BaseModel):
    private_token: str = ""
    url: str = "https://gitlab.com"


class Json(pydantic.BaseModel):
    indent: int = 2
    extensions: list[str] = [".json"]


class Toml(pydantic.BaseModel):
    extensions: list[str] = [".toml"]


class Yaml(pydantic.BaseModel):
    explicit_start: Optional[bool] = False
    extensions: list[str] = [".yaml", ".yml"]


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__", env_prefix="rcmt_", extra="allow"
    )

    database: Database = Database()
    dry_run: bool = False
    git: Git = Git()
    github: Github = Github()
    gitlab: Gitlab = Gitlab()
    # Add _ because json is a reserved field of pydantic
    json_: Json = Field(alias="json", default=Json())
    log_format: Optional[str] = None
    log_level: str = "info"
    pr_title_prefix: str = "rcmt:"
    pr_title_body: str = "apply matcher {matcher_name}"
    pr_title_suffix: str = ""
    toml: Toml = Toml()
    yaml: Yaml = Yaml()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Override in order to let environment variables take precedence over other
        configuration settings by returning `env_settings` first.
        """
        return env_settings, init_settings, dotenv_settings, file_secret_settings


def read_config_from_file(path: str) -> Config:
    data = {}
    if path != "":
        with open(path, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

    return Config(**data)
