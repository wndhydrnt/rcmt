import datetime
import importlib.machinery
import importlib.util
import random
import string
import sys
from typing import Optional

from rcmt import matcher, source


class Run:
    def __init__(
        self,
        name: str,
        auto_merge=False,
        auto_merge_after: Optional[datetime.timedelta] = None,
        branch_name: str = "",
        pr_body: str = "",
        pr_title="",
    ):
        self.auto_merge = auto_merge
        self.auto_merge_after = auto_merge_after
        self.branch_name = branch_name
        self.pr_body = pr_body
        self.pr_title = pr_title
        self.name = name

        self.matchers: list[matcher.Base] = []
        self.packages: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def add_matcher(self, m: matcher.Base):
        self.matchers.append(m)

    def add_package(self, name: str):
        self.packages.append(name)

    def branch(self, prefix: str) -> str:
        if self.branch_name != "":
            return self.branch_name

        return f"{prefix}{self.name}"

    def match(self, repo: source.Repository) -> bool:
        for m in self.matchers:
            if m.match(repo) is False:
                return False

        return True


def read(path: str) -> Run:
    rndm = "".join(random.choice(string.ascii_lowercase) for _ in range(8))
    mod_name = f"rcmt_run_{rndm}"
    loader = importlib.machinery.SourceFileLoader(mod_name, path)
    spec = importlib.util.spec_from_loader(mod_name, loader)
    assert spec is not None
    new_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = new_module
    loader.exec_module(new_module)
    try:
        run = new_module.run  # type: ignore # because the content of module is not known
        if not isinstance(run, Run):
            raise RuntimeError(
                f"Run file {path} defines variable 'run' but is not of type Run"
            )

        return new_module.run  # type: ignore # because the content of module is not known
    except AttributeError:
        raise RuntimeError(f"Run file {path} does not define variable 'run'")
