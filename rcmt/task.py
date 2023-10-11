import datetime
import hashlib
import importlib.machinery
import importlib.util
import os.path
import random
import string
import sys
from typing import Callable, Optional

from slugify import slugify

from rcmt import context
from rcmt.fs import FileProxy
from rcmt.typing import Action, Matcher


class TaskRegistry:
    """
    TaskRegistry stores all loaded Tasks.
    """

    def __init__(self):
        self.task_path: Optional[str] = None
        self.tasks: list[Task] = []

    def register(self, task: "Task") -> None:
        """
        register adds a Task to the registry and calculates its checksum.

        :param task: The Task to register.
        """
        if self.task_path is None:
            raise RuntimeError("Task path must be set during task registration")

        for t in self.tasks:
            if t.name == task.name:
                raise RuntimeError(f"Task '{task.name}' already registered")

        checksum = hashlib.md5()
        with open(self.task_path) as f:
            while True:
                line = f.readline()
                if line == "":
                    break

                checksum.update(line.encode("utf-8"))

        task.checksum = checksum.hexdigest()
        task.set_path(os.path.dirname(self.task_path))
        self.tasks.append(task)


# registry is the single instance of TaskRegistry used by rcmt. Tasks call the instance
# in the __exit__ method of their context manager ("with" statement).
registry = TaskRegistry()


def register_task(task: "Task") -> None:
    registry.register(task)


class Task:
    """A Task connects Actions with repositories.

    rcmt reads the Task, finds matching repositories and then applies its Actions to
    each repository.

    Args:
        name: The name of the Task. rcmt uses the name to identify a task.
        auto_merge: rcmt automatically merges a pull request on its next run. The
                    pull request must pass all its checks.
        auto_merge_after: A duration after which to automatically merge a pull request.
                          Requires `auto_merge` to be set to `true`.
        branch_name: Name of the branch in git. Defaults to `branch_prefix` + `name`.
        change_limit: Limits the number of changes per run of the Task. A change is
                      either a pull request created or merged. Helps to reduce the
                      load on a CI/CD system when a Task would create a lot of pull
                      requests at the same time. Defaults to ``None`` which means no
                      limit.
        commit_msg: Message to use when committing changes via git.
        delete_branch_after_merge: If `True`, rcmt will delete the branch after it has
                                   been merged. Defaults to `True`.
        enabled: If `False`, disables the task. Handy if a task needs to be stopped
                 temporarily. Defaults to `True`.
        labels: List of strings to add as labels to a pull request. Labels are set on
                creation of a pull request. Subsequent updates of the labels will only
                affect new pull requests.
        merge_once: If `True`, rcmt does not create another pull request if it created a
                    pull request for the same branch before and that pull request has
                    been merged.
        pr_body: Define a custom body of a pull request.
        pr_title: Set a custom title for a pull request.

    Example:
        ```python
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
        ```
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
        labels: Optional[list[str]] = None,
    ):
        self.auto_merge = auto_merge
        self.auto_merge_after = auto_merge_after
        self.branch_name = branch_name
        self.change_limit = change_limit
        self.commit_msg = commit_msg
        self.delete_branch_after_merge = delete_branch_after_merge
        self.enabled = enabled
        self.labels = labels
        self.merge_once = merge_once
        self.name = name
        self.pr_body = pr_body
        self.pr_title = pr_title

        self.actions: list[Action] = []
        self.changes_total: int = 0
        self.checksum: str = ""
        self.failure_count: int = 0
        self.file_proxies: list[FileProxy] = []
        self.matchers: list[Matcher] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Do not register if an exception occurred
        if exc_val is not None:
            return

        register_task(task=self)

    def add_action(self, a: Callable[[str, dict], None]) -> None:
        """Add an Action to apply to every matching repository.

        Args:
            a: The Action.
        """
        self.actions.append(a)

    def add_matcher(self, m: Callable[[context.Context], bool]) -> None:
        """Add a Matcher that matches repositories.

        Args:
            m: The matcher to add.
        """
        self.matchers.append(m)

    def branch(self, prefix: str) -> str:
        if self.branch_name != "":
            return self.branch_name

        return f"{prefix}{slugify(self.name)}"

    def has_reached_change_limit(self) -> bool:
        if self.change_limit is None:
            return False

        return self.changes_total >= self.change_limit

    def load_file(self, path: str) -> FileProxy:
        """Returns a proxy that an Action can use to load a file.

        Args:
            path: Path to the file to load. Relative to the file that contains the Task.
        """
        fp = FileProxy(path)
        self.file_proxies.append(fp)
        return fp

    def match(self, ctx: context.Context) -> bool:
        for m in self.matchers:
            if m(ctx) is False:
                return False

        return True

    def set_path(self, path: str):
        for fp in self.file_proxies:
            fp.set_path(path)


class Run(Task):
    """
    Run is an alias of Task.

    Provides backwards compatibility with task files written for rcmt <= 0.15.3.
    """

    pass


def read(path: str) -> None:
    rndm = "".join(random.choice(string.ascii_lowercase) for _ in range(8))
    mod_name = f"rcmt_task_{rndm}"
    loader = importlib.machinery.SourceFileLoader(mod_name, path)
    spec = importlib.util.spec_from_loader(mod_name, loader)
    assert spec is not None
    new_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = new_module
    try:
        registry.task_path = path
        loader.exec_module(new_module)
    except Exception as e:
        raise RuntimeError(f"Import failed with {e.__class__.__name__}: {str(e)}")
    finally:
        registry.task_path = None
