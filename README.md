# rcmt

<div align="center">

[![pypi](https://img.shields.io/pypi/v/rcmt.svg)](https://pypi.org/project/rcmt/)
[![python](https://img.shields.io/pypi/pyversions/rcmt.svg)](https://pypi.org/project/rcmt/)
[![docs](https://readthedocs.org/projects/rcmt/badge/?version=stable)](https://readthedocs.org/projects/rcmt/?badge=stable)

</div>

rcmt automates refactorings across many repositories.

Write Python code to define how the content of files should look like. Then let rcmt
apply the changes across repositories and create pull requests.


## Features

- **Mass Refactoring** - create, update or delete files across many repositories.
- **Automation** - automatic creation of merge requests in repositories; optionally
  merge them automatically if approved and all checks have passed.
- **Flexibility** - call third-party APIs or integrate libraries.

## The Task file

A Task file tells rcmt which repositories to modify. It is written in Python.

```python
from rcmt import Task, Context, register_task


# Replace with your repository.
REPOSITORY = "github.com/wndhydrnt/rcmt-example"

# A Task bundles the code that determines which repositories to modify and how to modify
# them. It is a regular Python class that extends the base class `Task`.
class HelloWorld(Task):
    name = "hello-world"
    pr_title = "rcmt Hello World"
    pr_body = """This pull request has been created as part of the how-to guide:

https://rcmt.readthedocs.io/get-started/create-a-task/
"""

    # The `filter` method determines which repositories to modify. It is called by rcmt
    # for each repository.
    def filter(self, ctx: Context) -> bool:
        return ctx.repo.full_name == REPOSITORY

    # The `apply` method contains the code that modifies files in a repository. In this
    # example, the `own` function creates the file `hello-world.txt` with the content
    # `Hello World` in the root of the repository. `target` is not an absolute path
    # because rcmt automatically sets the current working directory (`cwd`) to the
    # checkout of the repository.
    def apply(self, ctx: Context) -> None:
        with open("hello-world.txt", "w+") as f:
            f.write("Hello World")


# Register the task with rcmt so rcmt knows about it.
register_task(HelloWorld())
```

## What's next

- [Tutorial](https://rcmt.readthedocs.io/en/stable/get-started/tutorial/)
- [Learn how rcmt works](https://rcmt.readthedocs.io/en/stable/get-started/how-it-works/)
- [Features](https://rcmt.readthedocs.io/en/stable/features/events/)
- [Examples](https://rcmt.readthedocs.io/en/stable/examples/simple/)
- [Reference](https://rcmt.readthedocs.io/en/stable/reference/configuration/)

## Contributing

[Learn how to contribute code to rcmt](https://rcmt.readthedocs.io/en/stable/contributing/)
