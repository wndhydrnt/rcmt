import datetime
from typing import Optional

import pydantic


class AbsentAction(pydantic.BaseModel):
    target: str


class DeleteKeyAction(pydantic.BaseModel):
    key: str
    target: str


class DeleteLineInFileAction(pydantic.BaseModel):
    line: str
    selector: str


class ExecAction(pydantic.BaseModel):
    exec_path: str
    selector: str
    timeout: int = 120


class LineInFileAction(pydantic.BaseModel):
    line: str
    selector: str


class MergeAction(pydantic.BaseModel):
    content: str
    merge_strategy: str = "replace"
    selector: str


class OwnAction(pydantic.BaseModel):
    content: str
    target: str


class ReplaceInLineAction(pydantic.BaseModel):
    search: str
    replace: str
    selector: str
    flags: int = 0


class SeedAction(pydantic.BaseModel):
    content: str
    target: str


class Actions(pydantic.BaseModel):
    absent: list[AbsentAction] = []
    delete_key: list[DeleteKeyAction] = []
    delete_line_in_file: list[DeleteLineInFileAction] = []
    exec: list[ExecAction] = []
    line_in_file: list[LineInFileAction] = []
    merge: list[MergeAction] = []
    own: list[OwnAction] = []
    replace_in_line: list[ReplaceInLineAction] = []
    seed: list[SeedAction] = []


class FileExistsMatcher(pydantic.BaseModel):
    path: str


class LineInFileMatcher(pydantic.BaseModel):
    path: str
    search: str


class RepoNameMatcher(pydantic.BaseModel):
    search: str


class Matchers(pydantic.BaseModel):
    file_exists: list[FileExistsMatcher] = []
    line_in_file: list[LineInFileMatcher] = []
    repo_name: list[RepoNameMatcher] = []


class Schema(pydantic.BaseModel):
    """
    rcmt
    """

    actions: Actions
    auto_merge: bool = False
    auto_merge_after: Optional[datetime.timedelta] = None
    branch_name: str = ""
    commit_msg: str = "Applied actions"
    matchers: Matchers
    merge_once: bool = False
    name: str
    pr_body: str = ""
    pr_title: str = ""

    class Config:
        title = "rcmt"
