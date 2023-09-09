"""
This file demonstrates how to refactor code with Semgrep.

Support for Semgrep is experimental to better understand how useful the integration is
and how it works in production.
"""
from typing import IO

from rcmt import Task
from rcmt.action import Action
from rcmt.action.semgrep import Semgrep
from rcmt.matcher import RepoName
from rcmt.util import iglob


class SysModuleImport(Action):
    """
    Add statement "import sys" if it is missing.
    """

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        for path in iglob(root=repo_path, selector="**/*.py"):
            with open(path) as f:
                do = self.needs_import_sys(f)
                if do is False:
                    continue

                f.seek(0)
                data = f.read()

            with open(path, mode="w") as f:
                f.write("import sys\n" + data)

    @staticmethod
    def needs_import_sys(f: IO) -> bool:
        has_import = False
        has_exit = False
        for line in f.readlines():
            if line == "import sys":
                has_import = True

            if "sys.exit(" in line:
                has_exit = True

        return has_exit and not has_import


with Task("Semgrep Example") as task:
    # Match a specific repository.
    task.add_matcher(RepoName("^github.com/MyOrg/example$"))

    # Use Semgrep to refactor Python files. The rules that define what to refactor are
    # stored in the file semgrep-rules.yaml.
    task.add_action(
        Semgrep(rules=task.load_file("semgrep-rules.yaml"), selector="**/*.py")
    )
    # Semgrep can refactor a line, but does not add the necessary import statement.
    # This Action does that.
    task.add_action(SysModuleImport())
