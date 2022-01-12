import datetime
import importlib.machinery
import importlib.util
import random
import string
import sys
from typing import Optional

from rcmt import matcher, source


class Run:
    """
    A Run connects packages with repositories. rcmt reads the Run, finds repositories
    and packages and then applies these packages to each repository.

    :param name: The name of the Run. rcmt uses the name to identify a run.
    :param auto_merge: rcmt automatically merges a pull request on its next run. The
                       pull request must pass all its checks.
    :param auto_merge_after: A duration after which to automatically merge a Pull
                             Request. Requires ``auto_merge`` to be set to ``true``.
    :param branch_name: Name of the branch in git. Defaults to ``branch_prefix`` +
                        ``name``.
    :param merge_once: If ``True``, rcmt does not create another pull request if it
                       created a pull request for the same branch before and that pull
                       request has been merged.
    :param pr_body: Define a custom body of a pull request.
    :param pr_title: Set a custom title for a pull request.

    **Example**

    .. code-block:: python

       from datetime import timedelta

       from rcmt import Run
       from rcmt.matcher import FileExists, RepoName

       with Run(
           name="python-defaults",
           auto_merge=True,
           auto_merge_after=timedelta(days=7)
       ) as run:
           run.add_matcher(FileExists("pyproject.toml"))
           run.add_matcher(RepoName("^github.com/wndhydrnt/rcmt$"))

           run.add_package("flake8")

           run.pr_title = "A custom PR title"
           run.pr_body = '''A custom PR title.
           It supports multiline strings.'''
    """

    def __init__(
        self,
        name: str,
        auto_merge: bool = False,
        auto_merge_after: Optional[datetime.timedelta] = None,
        branch_name: str = "",
        merge_once: bool = False,
        pr_body: str = "",
        pr_title: str = "",
    ):
        self.auto_merge = auto_merge
        self.auto_merge_after = auto_merge_after
        self.branch_name = branch_name
        self.pr_body = pr_body
        self.pr_title = pr_title
        self.merge_once = merge_once
        self.name = name

        self.matchers: list[matcher.Base] = []
        self.packages: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def add_matcher(self, m: matcher.Base) -> None:
        """
        Add a Matcher that matches repositories.

        :param m: The matcher to add.
        """
        self.matchers.append(m)

    def add_package(self, name: str) -> None:
        """
        Add a Package to apply to every matching repository.

        :param name: The name of the Package.
        """
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
