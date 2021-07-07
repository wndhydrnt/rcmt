import glob
import os
import string
from typing import Optional

import pydantic
import structlog
import yaml

from rcmt import action

log = structlog.get_logger()


class PackageInvalidError(RuntimeError):
    pass


class ActionWrapper:
    def __init__(self, name: str, pattern: str, tpl: str, act: action.Action):
        """

        :param name: Name of the file to which the Action applies.
        :param pattern: Glob pattern to select the files to which to apply the action.
        :param tpl: Raw data of the file to which the action applies. Passes the data to `string.Template`.
        :param act: Action to apply.
        """
        self.name = name
        self.pattern = pattern
        self.tpl = string.Template(tpl)
        self.action = act

    def apply(self, work_dir: str, mapping: dict):
        pattern = os.path.join(work_dir, self.pattern)
        for path in glob.iglob(pattern, recursive=True):
            self.action.apply(path, self.tpl.substitute(mapping))


class ManifestAction(pydantic.BaseModel):
    action: str
    file: str
    opts: dict = {}
    pattern: Optional[str]


class Manifest(pydantic.BaseModel):
    actions: list[ManifestAction]
    name: str


class Package:
    def __init__(self, name):
        self.name = name
        self.actions: list[ActionWrapper] = []


class PackageReader:
    def __init__(
        self,
        action_registry: action.Registry,
        encoding_registry: action.EncodingRegistry,
    ):
        self.action_registry = action_registry
        self.encoding_registry = encoding_registry

    def read_package(self, path: str) -> Package:
        log.debug("reading package from directory", dir=path)
        manifest_path = os.path.join(path, "manifest.yaml")
        if not os.path.isfile(manifest_path):
            raise PackageInvalidError("manifest.yaml not found")

        with open(manifest_path, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        manifest = Manifest(**data)
        pkg = Package(manifest.name)
        for ma in manifest.actions:
            tpl_path = os.path.join(path, ma.file)
            if not os.path.isfile(tpl_path):
                raise PackageInvalidError("missing template file in package")

            a = self.action_registry.create(ma.action, self.encoding_registry, ma.opts)
            with open(tpl_path) as f:
                data = f.read()

            pattern = ma.pattern
            if pattern is None:
                pattern = ma.file

            pkg.actions.append(ActionWrapper(ma.file, pattern, data, a))

        return pkg

    def read_packages(self, path: str) -> list[Package]:
        log.debug("reading packages", root_dir=path)
        packages = []
        for entry in os.listdir(path):
            package_path = os.path.join(path, entry)
            if not os.path.isdir(package_path):
                continue

            packages.append(self.read_package(package_path))

        return packages
