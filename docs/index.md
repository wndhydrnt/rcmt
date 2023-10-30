# rcmt

rcmt automates refactorings across many repositories.

Write Python code to define how the content of files should look like. Then let rcmt
apply the changes and create merge requests.

## Features

- **Mass Refactoring** - create, update or delete files across many repositories.
- **Automation** - automatic creation of merge requests in repositories; optionally
  merge them automatically if approved and all checks have passed.
- **Flexibility** - call third-party APIs or integrate libraries.

## Quick Start

### Prerequisites

- Python 3.9 or higher (verify with `python --version`).
- A repository on GitHub or GitLab to modify.
- A [GitHub Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token)
  or a [GitLab Access Token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#create-a-personal-access-token).

### Installation

```shell
pip install rcmt
rcmt version
```

Output

```
0.23.1
```

### Write the Task file

Create the file `task.py` and add the following content:

```python title="task.py"
from rcmt import Task, Context, register_task
from rcmt.action import own
from rcmt.filter import repo_name


class HelloWorld(Task):  # (1)!
    name = "hello-world"
    pr_title = "rcmt Hello World"
    pr_body = """This pull request has been created as part of the how-to guide:

https://rcmt.readthedocs.io/get-started/create-a-task/
"""

    def filter(self, ctx: Context) -> bool:  # (2)!
        return repo_name(ctx=ctx, search="^github.com/wndhydrnt/rcmt-example$")

    def apply(self, ctx: Context) -> None:  # (3)!
        own(ctx=ctx, content="Hello World", target="hello-world.txt")


register_task(HelloWorld())  # (4)!
```

1.  A Task bundles the code that determines which repositories to modify and how to
    modify them. It is a regular Python class that extends the base class `Task`.
2.  The `filter` method determines which repositories to modify. It is called by rcmt
    for each repository.
3.  The `apply` method contains the code that modifies files in a repository. In this
    example, the `own` function creates the file `hello-world.txt` with the content
    `Hello World` in the root of the repository.
4.  Register the task with rcmt so rcmt knows about it.

### Run rcmt

=== "GitHub"

    ```shell
    RCMT_GITHUB__ACCESS_TOKEN=xxxxx rcmt run ./task.py
    ```

=== "GitLab"

    ```shell
    RCMT_GITLAB__PRIVATE_TOKEN=xxxxx rcmt run ./task.py
    ```

Output

=== "GitHub"

    ```
    2023-09-26T19:57:20.215102Z [info     ] Matched repository             repository=github.com/wndhydrnt/rcmt-example task=rcmt-example
    2023-09-26T19:57:24.866457Z [info     ] Create pull request            repo=github.com/wndhydrnt/rcmt-example
    2023-09-26T19:57:25.637469Z [info     ] Finished processing of repositories repository_count=1
    ```

=== "GitLab"

    ```
    2023-09-26T19:57:20.215102Z [info     ] Matched repository             repository=gitlab.com/wandhydrant/rcmt-example task=rcmt-example
    2023-09-26T19:57:24.866457Z [info     ] Create pull request            repo=gitlab.com/wandhydrant/rcmt-example
    2023-09-26T19:57:25.637469Z [info     ] Finished processing of repositories repository_count=1
    ```
### View and merge the pull request

rcmt has created a pull request. Check GitHub or GitLab to inspect the changes.
