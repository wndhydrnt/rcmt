import hashlib
import importlib.machinery
import importlib.util
import os
import random
import string
import sys
from typing import Any, Hashable, Optional

import structlog

from .. import encoding
from . import action
from .manifest import Manifest

log = structlog.get_logger()


class PackageInvalidError(RuntimeError):
    pass


class Package:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.actions: list[action.Action] = []


class PackageReader:
    def __init__(self, encoding_registry: encoding.Registry):
        self.encoding_registry = encoding_registry

    def read_package(self, path: str) -> Package:
        log.debug("reading package from directory", dir=path)
        manifest_path = os.path.join(path, "manifest.py")
        if not os.path.isfile(manifest_path):
            raise PackageInvalidError("manifest.py not found")

        m = load_manifest(manifest_path)
        pkg = Package(m.name, path)
        for ma in m.actions:
            if isinstance(ma, action.EncodingAware):
                ma.encodings = self.encoding_registry

            pkg.actions.append(ma)

        return pkg

    def read_packages(self, paths: list[str]) -> list[Package]:
        packages = []
        for path in paths:
            log.debug("reading packages", root_dir=path)
            for entry in os.listdir(path):
                package_path = os.path.join(path, entry)
                if not os.path.isdir(package_path):
                    continue

                packages.append(self.read_package(package_path))

        return packages


def load_manifest(path: str) -> Manifest:
    rndm = "".join(random.choice(string.ascii_lowercase) for _ in range(8))
    mod_name = f"rcmt_manifest_{rndm}"
    loader = importlib.machinery.SourceFileLoader(mod_name, path)
    spec = importlib.util.spec_from_loader(mod_name, loader)
    assert spec is not None
    new_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = new_module
    loader.exec_module(new_module)
    try:
        m = new_module.manifest  # type: ignore # because the content of module is not known
        if not isinstance(m, Manifest):
            raise RuntimeError(
                f"Run file {path} defines variable 'manifest' but is not an instance of class Manifest"
            )

        return new_module.manifest  # type: ignore # because the content of module is not known
    except AttributeError:
        raise RuntimeError(f"Manifest file {path} does not define variable 'manifest'")
