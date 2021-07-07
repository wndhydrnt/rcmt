import io
import json
import os
import pathlib
from typing import Any, Callable, MutableMapping, TextIO

import mergedeep
import toml
import yaml


class Encoding:
    def decode(self, file: TextIO) -> Any:
        raise NotImplementedError("class does not implement Encoding.decode()")

    def encode(self, file: TextIO, data: dict) -> None:
        raise NotImplementedError("class does not implement Encoding.encode()")

    def merge(self, repo_data: Any, pkg_data: Any) -> Any:
        raise NotImplementedError("class does not implement Encoding.merge()")


class EncodingRegistry:
    def __init__(self):
        self.encodings: list[dict] = []

    def add(self, enc: Encoding, extensions: list[str]) -> None:
        self.encodings.append({"encoding": enc, "extensions": extensions})

    def get_for_extension(self, ext: str) -> Encoding:
        for entry in self.encodings:
            if ext in entry["extensions"]:
                return entry["encoding"]

        raise RuntimeError(f"No encoding registered for extension {ext}")


class Json(Encoding):
    def __init__(self, indent: int = 0):
        self.indent = indent

    def decode(self, file: TextIO) -> dict:
        return json.load(file)

    def encode(self, file: TextIO, data: MutableMapping) -> None:
        json_str = json.dumps(data, indent=self.indent)
        file.write(json_str + "\n")

    def merge(self, repo_data: dict, pkg_data: dict) -> MutableMapping:
        cp = repo_data.copy()
        return mergedeep.merge(cp, pkg_data, strategy=mergedeep.Strategy.ADDITIVE)


class Yaml(Encoding):
    def __init__(self, explicit_start=False):
        self.explicit_start = explicit_start

    def decode(self, file: TextIO) -> dict:
        return yaml.load(file, Loader=yaml.FullLoader)

    def encode(self, file: TextIO, data: MutableMapping) -> None:
        yaml.dump(data, file, explicit_start=self.explicit_start)

    def merge(self, repo_data: dict, pkg_data: dict) -> MutableMapping:
        cp = repo_data.copy()
        return mergedeep.merge(cp, pkg_data, strategy=mergedeep.Strategy.ADDITIVE)


class Toml(Encoding):
    def decode(self, file: TextIO) -> MutableMapping:
        return toml.load(file)

    def encode(self, file: TextIO, data: MutableMapping) -> None:
        toml.dump(data, file)

    def merge(self, repo_data: dict, pkg_data: dict) -> MutableMapping:
        cp = repo_data.copy()
        return mergedeep.merge(cp, pkg_data, strategy=mergedeep.Strategy.ADDITIVE)


class Action:
    def apply(self, repo_file_path: str, tpl_data: str) -> None:
        raise NotImplementedError("class does not implement Action.apply()")


class Own(Action):
    def __init__(self, seed_only: bool) -> None:
        self.seed_only = seed_only

    @staticmethod
    def factory_own(er: EncodingRegistry, opts: dict):
        return Own(False)

    @staticmethod
    def factory_seed(er: EncodingRegistry, opts: dict):
        return Own(True)

    def apply(self, repo_file_path: str, tpl_data: str) -> None:
        if os.path.isfile(repo_file_path) and self.seed_only:
            return

        with open(repo_file_path, "w+") as f:
            f.write(tpl_data)


class Merge(Action):
    def __init__(self, encodings: EncodingRegistry):
        self.encodings = encodings

    @staticmethod
    def factory(er: EncodingRegistry, opts: dict):
        return Merge(er)

    def apply(self, repo_file_path: str, tpl_data: str) -> None:
        ext = pathlib.Path(repo_file_path).suffix
        enc = self.encodings.get_for_extension(ext)
        with open(repo_file_path, "r") as f:
            orig_data = enc.decode(f)

        tpl = enc.decode(io.StringIO(tpl_data))
        merged_data = enc.merge(orig_data, tpl)
        with open(repo_file_path, "w") as f:
            enc.encode(f, merged_data)


class DeleteKeys(Action):
    def __init__(self, encodings: EncodingRegistry):
        self.encodings = encodings

    @staticmethod
    def factory(er: EncodingRegistry, opts: dict):
        return DeleteKeys(er)

    def apply(self, repo_file_path: str, tpl_data: str) -> None:
        ext = pathlib.Path(repo_file_path).suffix
        enc = self.encodings.get_for_extension(ext)
        with open(repo_file_path, "r") as f:
            orig_data: dict = enc.decode(f)

        query: dict = enc.decode(io.StringIO(tpl_data))
        new_data = self.process_recursive(query, orig_data)
        with open(repo_file_path, "w") as f:
            enc.encode(f, new_data)

    @classmethod
    def process_recursive(cls, query: dict, data: dict) -> dict:
        for qk in query.keys():
            if qk not in data:
                continue

            if isinstance(query[qk], dict) and isinstance(data[qk], dict):
                data[qk] = cls.process_recursive(query[qk], data[qk])
            else:
                del data[qk]

        return data


class Registry:
    def __init__(self):
        self.factories: dict[str, Callable[[EncodingRegistry, dict], Action]] = {}

    def add(self, name: str, factory: Callable[[EncodingRegistry, dict], Action]):
        self.factories[name] = factory

    def create(self, name: str, er: EncodingRegistry, opts: dict) -> Action:
        return self.factories[name](er, opts)
