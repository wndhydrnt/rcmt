import os.path
import tempfile
from typing import Any, Optional

import pydantic
import yaml
from pydantic.fields import Field


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


class Config(pydantic.BaseSettings):
    database: Database = Database()
    dry_run: bool = False
    git: Git = Git()
    github: Github = Github()
    gitlab: Gitlab = Gitlab()
    # Add _ because json is a reserved field of pydantic
    json_: Json = Field(alias="json", default=Json(), env="json")
    log_level: str = "info"
    pr_title_prefix: str = "rcmt:"
    pr_title_body: str = "apply matcher {matcher_name}"
    pr_title_suffix: str = ""
    toml: Toml = Toml()
    yaml: Yaml = Yaml()

    class Config:
        env_nested_delimiter = "__"
        env_prefix = "rcmt_"
        extra = pydantic.Extra.allow


def read_config_from_file(path: str) -> Config:
    data = {}
    if path != "":
        with open(path, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

    return Config(**data)
