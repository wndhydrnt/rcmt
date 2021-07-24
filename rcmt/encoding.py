"""
Encodings allow Actions to read various config file formats.
"""
import json
from typing import Any, MutableMapping, TextIO

import mergedeep
import toml
import yaml


class Encoding:
    """
    Encoding defines the API of each encoding.
    """

    def decode(self, file: TextIO) -> Any:
        """
        decode parses the content of a file-like object.

        :param file: File to parse.
        :return: Any
        """
        raise NotImplementedError("class does not implement Encoding.decode()")

    def encode(self, file: TextIO, data: dict) -> None:
        """
        encode writes data to a file-like object.

        :param file: File to write data to.
        :param data: Data to write to the file.
        :return: None
        """
        raise NotImplementedError("class does not implement Encoding.encode()")

    def merge(self, repo_data: Any, pkg_data: Any, strategy: mergedeep.Strategy) -> Any:
        """
        merge merges the data from a repository with the data from a package.

        :param repo_data: Data read from a file in a repository.
        :param pkg_data: Data read from a file in a package.
        :param strategy: The strategy to use when merging dicts. Not every encoding
                         needs to support this option.
        :return: Any
        """
        raise NotImplementedError("class does not implement Encoding.merge()")


class Registry:
    """
    Registry holds all known encodings and the file extensions each encoding supports.
    """

    def __init__(self):
        self.encodings: list[dict] = []

    def register(self, enc: Encoding, extensions: list[str]) -> None:
        """
        register registers an Encoding and its file extensions.

        :param enc: The Encoding to register.
        :param extensions: A list of file extensions, e.g. `[".yaml", ".yml"]`.
        :return: None
        """
        self.encodings.append({"encoding": enc, "extensions": extensions})

    def get_for_extension(self, ext: str) -> Encoding:
        """
        get_for_extension returns an Encoding for the given file extension.

        :param ext: The file extension to search for.
        :raises RuntimeError: If no Encoding has been registered for the file extension.
        :return: Encoding
        """
        for entry in self.encodings:
            if ext in entry["extensions"]:
                return entry["encoding"]

        raise RuntimeError(f"No encoding registered for extension {ext}")


class Json(Encoding):
    """
    Json supports json files.

    It uses Python's `json` module to decode and encode data.
    """

    def __init__(self, indent: int = 0):
        self.indent = indent

    def decode(self, file: TextIO) -> dict:
        return json.load(file)

    def encode(self, file: TextIO, data: MutableMapping) -> None:
        json_str = json.dumps(data, indent=self.indent)
        file.write(json_str + "\n")

    def merge(
        self, repo_data: dict, pkg_data: dict, strategy: mergedeep.Strategy
    ) -> MutableMapping:
        cp = repo_data.copy()
        return mergedeep.merge(cp, pkg_data, strategy=strategy)


class Yaml(Encoding):
    """
    Yaml supports yaml files.

    It uses `PyYAML` to decode and encode data.
    """

    def __init__(self, explicit_start=False):
        self.explicit_start = explicit_start

    def decode(self, file: TextIO) -> dict:
        return yaml.load(file, Loader=yaml.FullLoader)

    def encode(self, file: TextIO, data: MutableMapping) -> None:
        yaml.dump(data, file, explicit_start=self.explicit_start)

    def merge(
        self, repo_data: dict, pkg_data: dict, strategy: mergedeep.Strategy
    ) -> MutableMapping:
        cp = repo_data.copy()
        return mergedeep.merge(cp, pkg_data, strategy=strategy)


class Toml(Encoding):
    """
    Toml supports files written in Tom's Obvious, Minimal Language.
    """

    def decode(self, file: TextIO) -> MutableMapping:
        return toml.load(file)

    def encode(self, file: TextIO, data: MutableMapping) -> None:
        toml.dump(data, file)

    def merge(
        self, repo_data: dict, pkg_data: dict, strategy: mergedeep.Strategy
    ) -> MutableMapping:
        cp = repo_data.copy()
        return mergedeep.merge(cp, pkg_data, strategy=strategy)
