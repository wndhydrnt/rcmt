# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import datetime
import hashlib
import importlib.machinery
import importlib.util
import inspect
import os.path
import random
import string
import sys
from typing import Optional

import structlog
from slugify import slugify

from rcmt import Context

log: structlog.stdlib.BoundLogger = structlog.get_logger(package="task")


class Task:
    """A Task connects Actions with repositories.

    rcmt reads the Task, finds matching repositories and then applies its Actions to
    each repository.

    Attributes:
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
        from rcmt import Task, Context
        from rcmt.action import own
        from rcmt.filter import repo_name


        class HelloWorld(Task):
            name = "hello-world"
            pr_title = "rcmt Hello World"
            pr_body = '''This pull request has been created as part of the how-to guide:

        https://rcmt.readthedocs.io/get-started/create-a-task/
        '''

            def filter(self, ctx: Context) -> bool:
                return repo_name(ctx=ctx, search="^github.com/wndhydrnt/rcmt-example$")

            def apply(self, ctx: Context) -> None:
                own(ctx=ctx, content="Hello World", target="hello-world.txt")


        register_task(HelloWorld())
        ```
    """

    name: str
    auto_merge: bool = False
    auto_merge_after: Optional[datetime.timedelta] = None
    branch_name: str = ""
    change_limit: Optional[int] = None
    commit_msg: str = "Applied actions"
    delete_branch_after_merge: bool = True
    enabled: bool = True
    merge_once: bool = False
    pr_body: str = ""
    pr_title: str = ""
    labels: Optional[list[str]] = None

    _path: str = ""

    def apply(self, ctx: Context) -> None:
        """apply contains all logic that modifies files in a repository. The class that
        extends Task needs to override this method and implement the actual logic.

        rcmt calls this method if filter() returned true. It sets the current working
        directory (`cwd`) to the checkout of the repository.

        Args:
            ctx: The context that holds the current repository and additional
                 information.
        """
        raise NotImplementedError("Task does not implement method apply()")

    def filter(self, ctx: Context) -> bool:
        """filter determines if the task can be applied to the current repository. The
        class that extends Task needs to override this method and implement the actual
        logic.

        Args:
            ctx: The context that holds the current repository and additional
                 information.

        Returns:
            Boolean that indicates if this task should process the current repository.
        """
        raise NotImplementedError("Task does not implement method filter()")

    def load_file(self, path: str) -> str:
        """Returns a proxy that an Action can use to load a file.

        Args:
            path: Path to the file to load. Relative to the file that contains the Task.
        """
        with open(os.path.join(self._path, path)) as f:
            return f.read()

    def on_pr_closed(self, ctx: Context) -> None:
        """on_pr_closed gets called when a pull request is closed by rcmt.

        This can happen, for example, when the modifications have already been done in
        the default branch of a repository and the pull request is no longer needed.

        This method does nothing by default. A class that extends Task can override this
        method and implement custom logic, like sending an e-mail or posting a message.

        Args:
            ctx: The current context.
        """
        return None

    def on_pr_created(self, ctx: Context) -> None:
        """on_pr_closed gets called when a pull request is created by rcmt.

        This method does nothing by default. A class that extends Task can override this
        method and implement custom logic, like sending an e-mail or posting a message.

        Args:
            ctx: The current context.
        """
        return None

    def on_pr_merged(self, ctx: Context) -> None:
        """on_pr_merged gets called when a pull request is merged by rcmt.

        This method does nothing by default. A class that extends Task can override this
        method and implement custom logic, like sending an e-mail or posting a message.

        Args:
            ctx: The current context.
        """
        return None

    def set_path(self, path: str):
        self._path = os.path.abspath(os.path.dirname(path))


class TaskWrapper:
    def __init__(self, t: Task):
        self.task = t

        self.changes_total: int = 0
        self.checksum: str = ""
        self.failure_count: int = 0

    def apply(self, ctx: Context) -> None:
        self.task.apply(ctx=ctx)

    def branch(self, prefix: str) -> str:
        if self.task.branch_name != "":
            return self.task.branch_name

        return f"{prefix}{slugify(self.task.name)}"

    def filter(self, ctx: Context) -> bool:
        return self.task.filter(ctx=ctx)

    def has_reached_change_limit(self) -> bool:
        if self.task.change_limit is None:
            return False

        return self.changes_total >= self.task.change_limit

    @property
    def change_limit(self) -> Optional[int]:
        return self.task.change_limit

    @property
    def name(self) -> str:
        return self.task.name


class TaskRegistry:
    """
    TaskRegistry stores all loaded Tasks.
    """

    def __init__(self):
        self.task_path: Optional[str] = None
        self.tasks: list[TaskWrapper] = []

    def register(self, task: Task) -> None:
        """
        register adds a Task to the registry and calculates its checksum.

        :param task: The Task to register.
        """
        if self.task_path is None:
            log.debug(f"Path to Task no set - not registering Task {task.name}")
            return None

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

        task.set_path(self.task_path)
        wrapper = TaskWrapper(t=task)
        wrapper.checksum = checksum.hexdigest()
        self.tasks.append(wrapper)
        log.info(f"Registered Task {task.name}")


# registry is the single instance of TaskRegistry used by rcmt. `register_task` uses
# this registry.
registry = TaskRegistry()


def register_task(*tasks: Task) -> None:
    for t in tasks:
        registry.register(t)


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
        for name, obj in inspect.getmembers(new_module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, Task)
                and obj.__module__ == mod_name
            ):
                known = [wrapper.task.__class__.__name__ for wrapper in registry.tasks]
                if name not in known:
                    raise RuntimeError(
                        f"File '{path}' defines Task '{name}' but does not register it - use rcmt.register_task({name}())"
                    )

    except Exception as e:
        raise RuntimeError(f"Import failed with {e.__class__.__name__}: {str(e)}")
    finally:
        registry.task_path = None
