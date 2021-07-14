from typing import Optional

import pydantic


class DeleteKeyOptions(pydantic.BaseModel):
    key: str


class ExecOptions(pydantic.BaseModel):
    path: str
    timeout: int = 120


class MergeOptions(pydantic.BaseModel):
    source_file: str


class OwnOptions(pydantic.BaseModel):
    source_file: str


class SeedOptions(pydantic.BaseModel):
    source_file: str


class Action(pydantic.BaseModel):
    selector: str
    delete_key: Optional[DeleteKeyOptions]
    exec: Optional[ExecOptions]
    merge: Optional[MergeOptions]
    own: Optional[OwnOptions]
    seed: Optional[SeedOptions]

    @pydantic.root_validator
    def check_action_set(cls, values: dict):
        set_fields: list[str] = []
        for key, val in values.items():
            if key == "selector":
                continue

            if val is not None:
                set_fields.append(key)

        if len(set_fields) == 0:
            raise ValueError("No action set")

        if len(set_fields) > 1:
            raise ValueError(f"Multiple actions set: {', '.join(set_fields)}")

        return values

    @property
    def name(self) -> str:
        for field, value in self.__dict__.items():
            if field == "selector":
                continue

            if value is not None:
                return field

        raise RuntimeError("No action set")


class Manifest(pydantic.BaseModel):
    actions: list[Action]
    name: str
