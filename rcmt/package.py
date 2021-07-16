import hashlib
import os

import structlog
import yaml

from rcmt import action, encoding, manifest

log = structlog.get_logger()


class PackageInvalidError(RuntimeError):
    pass


class Package:
    def __init__(self, name):
        self.name = name
        self.actions: list[action.Action] = []
        self.checksum = None

    @property
    def version(self) -> str:
        if self.checksum is None:
            return ""

        return self.checksum.hexdigest()[0:8]


class PackageReader:
    def __init__(
        self,
        action_registry: action.Registry,
        encoding_registry: encoding.Registry,
    ):
        self.action_registry = action_registry
        self.encoding_registry = encoding_registry

    def read_package(self, path: str) -> Package:
        log.debug("reading package from directory", dir=path)
        manifest_path = os.path.join(path, "manifest.yaml")
        if not os.path.isfile(manifest_path):
            raise PackageInvalidError("manifest.yaml not found")

        checksum = hashlib.sha256(b"")
        with open(manifest_path, "r") as f:
            data_raw = f.read()
            checksum.update(data_raw.encode("utf-8"))
            data = yaml.load(data_raw, Loader=yaml.FullLoader)

        m = manifest.Manifest(**data)
        pkg = Package(m.name)
        for ma in m.actions:
            a = self.action_registry.create(ma.name, self.encoding_registry, ma, path)
            pkg.actions.append(a)

        pkg.checksum = checksum
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
