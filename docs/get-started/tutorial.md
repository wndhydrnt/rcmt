# Tutorial

rcmt Tasks are written in Python. This tutorial describes how to bootstrap a project
that contains the rcmt Tasks.

## Prerequisites

- A GitHub Access Token or a GitLab Access Token
- A repository on GitHub or GitLab to test rcmt with

## Install cookiecutter

[cookiecutter][] is a tool to bootstrap a project from a template.

[cookiecutter]: https://cookiecutter.readthedocs.io/en/stable/README.html

=== "Homebrew"

    ```shell
    brew install cookiecutter
    cookiecutter --help
    ```

=== "pipx"

    ```shell
    pip install pipx # If pipx has not been installed yet
    pipx ensurepath
    ```

More ways to install cookiecutter can be found in the [installation guide][] of the
cookiecutter docs.

[installation guide]: https://cookiecutter.readthedocs.io/en/stable/installation.html

## Bootstrap the repository

With cookiecutter installed, it can be executed to bootstrap a new project to from the
[cookiecutter-rcmt][] template.

The template requires some input from the user, like the name of the project and whether
to create the files needed to build a Docker image. 

[cookiecutter-rcmt]: https://github.com/wndhydrnt/cookiecutter-rcmt

=== "Homebrew"

    ```text
    cookiecutter https://github.com/wndhydrnt/cookiecutter-rcmt.git
    ```

=== "pipx"

    ```shell
    pipx run cookiecutter https://github.com/wndhydrnt/cookiecutter-rcmt.git
    ```

Output:

=== "Homebrew"

    ```text
      [1/3] Project Name (rcmt-tasks):
      [2/3] Python Package Name (rcmt_tasks):
      [3/3] Set up Docker (y/n) (y):
    # ...
    Successfully built rcmt-tasks
    Installing collected packages: ...
    ```

=== "pipx"

    ```text
      [1/3] Project Name (rcmt-tasks):
      [2/3] Python Package Name (rcmt_tasks):
      [3/3] Set up Docker (y/n) (y):
    # ...
    Successfully built rcmt-tasks
    Installing collected packages: ...
    ```

cookiecutter creates directories/files and also installs rcmt.

## Directory structure

Take a look at the generated directories and files:

```python
.
├── .dockerignore  # (1)!
├── .gitignore
├── Dockerfile  # (2)!
├── Makefile  # (3)!
├── README.md  # (4)!
├── pyproject.toml  # (5)!
├── rcmt_tasks  # (6)!
│   ├── __init__.py
│   └── example.py  # (7)!
├── tests  # (8)!
│   ├── __init__.py
│   └── test_example.py
├── rcmt_tasks.egg-info  # (9)!
└── venv  # (10)!
```

1.  `.dockerignore` contains files/directories that should not be copied into the Docker
    image. Created only if `Set up Docker` was answered with `y`. 
2. The `Dockerfile` from which to create a Docker image. Created only if
    `Set up Docker` was answered with `y`.
3.  `Makefile` contains commands for common actions, like build a Docker image or
    installing dependencies.
4.  `README.md` contains information about the project. Change as needed.
5.  `pyproject.toml` defines the Python project. Dependencies are defined here.
6.  `rcmt_tasks` is the Python module that contains all rcmt Tasks.
7.  `example.py` contains a Task as an example. Delete if not needed.
8.  `tests` contain unit tests of Tasks. Lean more about the
    [unit testing feature](../features/unit-testing.md).
9.  Python package information.
10. Files of the virtualenv. Contains rcmt and all its dependencies. More on it in the
    next section.

## Activate the virtualenv

To activate the virtualenv, run the following commands:

```shell
cd ./rcmt-tasks
# This activates the virtualenv in the local shell
source ./venv/bin/activate
rcmt version
```

A [virtualenv][] isolates binaries and dependencies of a project from the system-wide
installation of Python. Doing so avoids clashes between different versions of the same
Python package.

[virtualenv]: https://docs.python.org/3/library/venv.html

The virtualenv was created automatically by cookiecutter during the initialization of
the project.

## Create the first Task

The Task file contains the code that decides if a repository should be modified and how
to modify it.

Create the file `rcmt_tasks/hello_world.py` with the following content:

```python title="rcmt_tasks/hello_world.py"
from rcmt import Task, Context, register_task


# Replace with your repository.
REPOSITORY = "github.com/wndhydrnt/rcmt-example"


class HelloWorld(Task):
    name = "hello-world"
    pr_title = "rcmt Hello World"
    pr_body = """This pull request has been created as part of the how-to guide:

https://rcmt.readthedocs.io/get-started/create-a-task/
"""

    def filter(self, ctx: Context) -> bool:
        return ctx.repo.full_name == REPOSITORY

    def apply(self, ctx: Context) -> None:
        with open("hello-world.txt", "w+") as f:
            f.write("Hello World\n")


register_task(HelloWorld())
```

## Run the Task

With the Task file ready, supply the GitHub/GitLab Access Token and execute rcmt:

=== "GitHub"

    ```shell
    RCMT_GITHUB__ACCESS_TOKEN=xxxxx rcmt run ./rcmt_tasks/hello_world.py
    ```

=== "GitLab"

    ```shell
    RCMT_GITLAB__PRIVATE_TOKEN=xxxxx rcmt run ./rcmt_tasks/hello_world.py
    ```

rcmt has created a pull request at the repository.
