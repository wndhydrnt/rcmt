import datetime
import hashlib
import importlib.machinery
import importlib.util
import os.path
import random
import string
import sys
from typing import Optional

from slugify import slugify

from rcmt import action, matcher, source
from rcmt.fs import FileProxy


class Task:
    """
    A Task connects Actions with repositories. rcmt reads the Task, finds matching
    repositories and then applies its Actions to each repository.

    :param name: The name of the Task. rcmt uses the name to identify a task.
    :param auto_merge: rcmt automatically merges a pull request on its next run. The
                       pull request must pass all its checks.
    :param auto_merge_after: A duration after which to automatically merge a Pull
                             Request. Requires ``auto_merge`` to be set to ``true``.
    :param branch_name: Name of the branch in git. Defaults to ``branch_prefix`` +
                        ``name``.
    :param change_limit: Limits the number of changes per run of the Task. A change is
                         either a pull request created or merged. Helps to reduce the
                         load on a CI/CD system when a Task would create a lot of pull
                         requests at the same time. Defaults to ``None`` which means no
                         limit.
    :param commit_msg: Message to use when committing changes via git.
    :param delete_branch_after_merge: If ``True``, rcmt will delete the branch after it
                                      has been merged. Defaults to ``True``.
    :param enabled: If ``False``, disables the task. Handy if a task needs to be stopped
                    temporarily. Defaults to ``True``.
    :param merge_once: If ``True``, rcmt does not create another pull request if it
                       created a pull request for the same branch before and that pull
                       request has been merged.
    :param pr_body: Define a custom body of a pull request.
    :param pr_title: Set a custom title for a pull request.

    **Example**

    .. code-block:: python

       from datetime import timedelta

       from rcmt import Task
       from rcmt.matcher import FileExists, RepoName

       with Task(
           name="python-defaults",
           auto_merge=True,
           auto_merge_after=timedelta(days=7)
       ) as task:
           task.add_matcher(FileExists("pyproject.toml"))
           task.add_matcher(RepoName("^github.com/wndhydrnt/rcmt$"))

           task.pr_title = "A custom PR title"
           task.pr_body = '''A custom PR title.
           It supports multiline strings.'''
    """

    def __init__(
        self,
        name: str,
        auto_merge: bool = False,
        auto_merge_after: Optional[datetime.timedelta] = None,
        branch_name: str = "",
        change_limit: Optional[int] = None,
        commit_msg: str = "Applied actions",
        delete_branch_after_merge: bool = True,
        enabled: bool = True,
        merge_once: bool = False,
        pr_body: str = "",
        pr_title: str = "",
    ):
        self.auto_merge = auto_merge
        self.auto_merge_after = auto_merge_after
        self.branch_name = branch_name
        self.change_limit = change_limit
        self.commit_msg = commit_msg
        self.delete_branch_after_merge = delete_branch_after_merge
        self.enabled = enabled
        self.merge_once = merge_once
        self.name = name
        self.pr_body = pr_body
        self.pr_title = pr_title

        self.actions: list[action.Action] = []
        self.checksum: str = ""
        self.file_proxies: list[FileProxy] = []
        self.matchers: list[matcher.Base] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def add_action(self, a: action.Action) -> None:
        """
        Add an Action to apply to every matching repository.

        :param a: The Action.
        """
        self.actions.append(a)

    def add_matcher(self, m: matcher.Base) -> None:
        """
        Add a Matcher that matches repositories.

        :param m: The matcher to add.
        """
        self.matchers.append(m)

    def branch(self, prefix: str) -> str:
        if self.branch_name != "":
            return self.branch_name

        return f"{prefix}{slugify(self.name)}"

    def load_file(self, path: str) -> FileProxy:
        """
        Returns a proxy that an Action can use to load a file.

        :param path: Path to the file to load. Relative to the file that contains the
                     Task.
        """
        fp = FileProxy(path)
        self.file_proxies.append(fp)
        return fp

    def match(self, repo: source.Repository) -> bool:
        for m in self.matchers:
            if m.match(repo) is False:
                return False

        return True

    def set_path(self, path):
        """
        Set the path to the Task.
        Forwards this path to all ``FileProxys`` created when calling the
        ``load_file`` function.
        rcmt calls this function when it loads a Task file.

        :param path: Path to the directory that contains the Task file.
        """
        for fp in self.file_proxies:
            fp.set_path(path)


class Run(Task):
    """
    Run is an alias of Task.

    Provides backwards compatibility with task files written for rcmt <= 0.15.3.
    """

    pass


def read(path: str) -> Task:
    checksum = hashlib.md5()
    with open(path) as f:
        while True:
            line = f.readline()
            if line == "":
                break

            checksum.update(line.encode("utf-8"))

    rndm = "".join(random.choice(string.ascii_lowercase) for _ in range(8))
    mod_name = f"rcmt_task_{rndm}"
    loader = importlib.machinery.SourceFileLoader(mod_name, path)
    spec = importlib.util.spec_from_loader(mod_name, loader)
    assert spec is not None
    new_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = new_module
    loader.exec_module(new_module)
    try:
        task = new_module.task  # type: ignore # because the content of module is not known
    except AttributeError:
        try:
            # Accept variable "run" for backward compatibility with versions <= 0.15.3
            task = new_module.run  # type: ignore # because the content of module is not known
        except AttributeError:
            raise RuntimeError(f"Task file {path} does not define variable 'task'")

    if not isinstance(task, Task):
        raise RuntimeError(
            f"Task file {path} defines variable 'task' but is not of type Task"
        )

    task.set_path(os.path.dirname(path))
    task.checksum = checksum.hexdigest()
    return task  # type: ignore # because the content of module is not known
