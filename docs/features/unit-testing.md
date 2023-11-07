# Unit testing

Unit tests verify the behavior of code before it is rolled out to production. rcmt comes
bundled with a test class that allows writing unit tests for a Task. It integrates with
the `unittest` module provided by Python.

## Usage

!!! tip

    Follow the [tutorial](../get-started/tutorial.md) to bootstrap a project.

### Directory Structure

Unit tests are created in the directory `tests` next to the directory that contains the
actual Tasks.

```
.
├── rcmt_tasks
│   ├── __init__.py
│   └── example.py
├── tests
│   ├── __init__.py
│   └── test_example.py
```

### Create the unit test

In order for Python to discover unit tests, a file that contains unit tests must adhere
to conventions:

- It must be created in the `tests` directory.
- Its file name must follow the pattern `test_<name>.py`.

```python title="tests/test_example.py"
from rcmt.unittest import TaskTestCase, Repository, File

from rcmt_tasks.example import Example


class ExampleTest(TaskTestCase):
    def test_filter(self):
        """Test that filter() matches."""
        task = Example()

        self.assertTaskFilterMatches(
            task=task,
            repo=Repository(name="example.dev/local/test")
        )
        self.assertTaskFilterDoesNotMatch(
            task=task,
            repo=Repository(name="github.com/wndhydrnt/rcmt")
        )

    def test_apply(self):
        """Test that apply() modifies the content of example.txt"""
        repo_before = Repository(
            "example.dev/local/test",
            File(content="some content", path="example.txt")
        )
        repo_after = Repository(
            "example.dev/local/test",
            File(content="example\n", path="example.txt")
        )

        task = Example()

        self.assertTaskModifiesRepository(
            task=task, before=repo_before, after=repo_after
        )
```

### Run the unit tests

```shell
python -m unittest discover -v
```

## What's next

- [Documentation of the `unittest` module from the Python standard library](https://docs.python.org/3/library/unittest.html)
- [Blog post on getting started with unit testing in Python](https://realpython.com/python-testing/)
