import sys

import click
import structlog

import rcmt
from rcmt.log import configure as configure_logging

# Default logging settings before any configuration has been read.
configure_logging(format=None, level="error")
log: structlog.stdlib.BoundLogger = structlog.get_logger()


run_help = """Apply a Task to all matching repositories of a remote Git host.

rcmt will find all matching repositories, clone them, apply each Action from
the Task file and create a pull request if files have changed.

Examples:

\b
# Apply Task "task.py"
rcmt run --config ./config.yaml ./task.py

\b
# Apply Task "task.py" to a single repository
rcmt run --config ./config.yaml --repository github.com/wndhydrnt/rcmt-test ./task.py

"""


@click.command(
    help=run_help,
    short_help="Apply a Task to all matching repositories of a remote Git host.",
)
@click.option("--config", help="Path to configuration file.", default="", type=str)
@click.option(
    "--repository",
    help="Name of a repository to which to apply the Task. Can be passed multiple times. rcmt will not query for all repositories if this option is set.",
    default=[],
    multiple=True,
)
@click.argument("task_file", nargs=-1)
def run(config: str, repository: tuple[str], task_file: list[str]):
    try:
        opts = rcmt.options_from_config(config)
        opts.task_paths = task_file
        opts.repositories = list(repository)
        configure_logging(format=opts.config.log_format, level=opts.config.log_level)
        result = rcmt.execute(opts)
        if result is False:
            exit(1)
    except Exception:
        log.exception("Unexpected error")
        exit(1)


validate_help = """Validate Task files.

Test that rcmt can load a task file. Useful during CI/CD before rolling out a change to
production.

No extra configuration is necessary to execute this command. A Task is loaded but no
calls to external APIs are made.

Note: Code in module scope of a Task will be executed during validation. A Task file
with the following content will print "Hello" when validated:

\b
print("Hello")
with Task(name="example") as task:
    # Add matchers/actions here



Examples:

\b
# Validate a single Task file
rcmt validate task.py

\b
# Validate multiple Task files
rcmt validate task1.py task2.py

\b
# Validate all Task files in a directory
rcmt validate tasks/*.py
"""


@click.command(help=validate_help, short_help="Validate Task files")
@click.argument("task_file", type=click.Path(), nargs=-1)
def validate(task_file: tuple[str]):
    if rcmt.validate(task_file_paths=task_file) is False:
        exit(1)


verify_help = """Verify a Task locally.

This command makes it possible to quickly verify that Matchers and Actions of a Task
work for a given repository.

The command queries the API of a Source and clones the repository, but does not create a
pull request.

Each execution of "verify" restores the cloned repository to a clean state before
applying Actions.

Examples:

\b
# Verify that Matchers and Actions in task.py work for the repository "github.com/wndhydrnt/rcmt"
rcmt verify gitlab.com/wandhydrant/rcmt-test task.py

Note: rcmt needs to query the API of a Source, like GitHub or GitLab, to execute the
Task.

\b
# Supply a GitHub Access Token
RCMT_GITHUB__ACCESS_TOKEN=xxx rcmt verify github.com/wndhydrnt/rcmt task.py

\b
# Supply a configuration file that contains an access token
rcmt verify --config config.yaml gitlab.com/wandhydrant/rcmt-test task.py
"""


@click.command(
    help=verify_help,
    short_help="Verify a Task locally. Useful during development.",
)
@click.option("--config", help="Path to configuration file.", default="", type=str)
@click.option(
    "--directory",
    help="Directory that stores cloned git repositories.",
    default=".rcmt",
    type=str,
)
@click.argument("repository", type=str)
@click.argument("task_file", type=str)
def verify(config: str, directory: str, repository: str, task_file: str):
    try:
        opts = rcmt.options_from_config(config)
        opts.task_paths = [task_file]
        configure_logging(format=opts.config.log_format, level=opts.config.log_level)
        rcmt.execute_verify(
            directory=directory, opts=opts, out=sys.stdout, repo_name=repository
        )
    except Exception:
        log.exception("Unexpected error")
        exit(1)


@click.command(
    help="Display version information",
    short_help="Display version information",
)
def version():
    click.echo(rcmt.__version__)


@click.group()
def main():
    pass


main.add_command(run)
main.add_command(validate)
main.add_command(verify)
main.add_command(version)
