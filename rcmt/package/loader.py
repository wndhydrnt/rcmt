import hashlib
import os.path
import urllib.parse

import git
import structlog

from rcmt.package import Package, PackageReader

log = structlog.stdlib.get_logger(package="package.loader")


class Base:
    def __init__(self, package_url: str):
        self.package_url = package_url

    def load(self, reader: PackageReader) -> Package:
        raise NotImplementedError("class does not implement Base.load()")


class Git(Base):
    def __init__(self, data_dir: str, package_url: str):
        super(Git, self).__init__(package_url)
        self.data_dir = data_dir

    def load(self, reader: PackageReader) -> Package:
        packages_dir = os.path.join(self.data_dir, "packages")
        if os.path.isdir(packages_dir) is False:
            log.debug("create packages data dir", loader="git")
            os.makedirs(packages_dir)

        url_parse = urllib.parse.urlparse(self.package_url)
        clone_url = f"{url_parse.netloc}{url_parse.path}"
        if url_parse.scheme != "":
            clone_url = f"{url_parse.scheme}://{clone_url}"

        clone_id = hashlib.md5(clone_url.encode("utf-8"))
        clone_dir = os.path.join(packages_dir, clone_id.hexdigest())
        query_items = urllib.parse.parse_qs(url_parse.query)
        try:
            ref = query_items["ref"][0]
        except KeyError:
            ref = "main"

        if os.path.isdir(clone_dir) is False:
            log.debug(
                "clone package", loader="git", src=self.package_url, dst=clone_dir
            )
            git.Repo.clone_from(clone_url, clone_dir, branch=ref)
        else:
            log.debug(
                "pull to update package",
                loader="git",
                src=self.package_url,
                dst=clone_dir,
            )
            git_repo = git.Repo(path=clone_dir)
            git_repo.git.pull()

        try:
            package_path = query_items["path"][0]
        except KeyError:
            package_path = ""

        return reader.read_package(os.path.join(clone_dir, package_path))


class Directory(Base):
    def load(self, reader: PackageReader) -> Package:
        return reader.read_package(os.path.abspath(self.package_url))


def create_loader(data_dir: str, package_url: str) -> Base:
    if package_url.startswith("git::"):
        log.debug("check out package using git", package=package_url)
        return Git(data_dir, package_url.lstrip("git::"))

    if os.path.isdir(os.path.abspath(package_url)):
        log.debug("read package from local filesystem", package=package_url)
        return Directory(package_url)

    raise RuntimeError(
        f"No loader for package URL '{package_url}' found - supports local directory and git"
    )
