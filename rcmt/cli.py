import logging
import sys

import click
import structlog

import rcmt

run_help = """Apply a Task to all matching repositories of a remote Git host.

rcmt will find all matching repositories, clone them, apply each Action from
the Task file and create a pull request if files have changed.

Examples:

\b
# Apply Task "task.py"
rcmt run --config ./config.yaml ./task.py
"""


@click.command(
    help=run_help,
    short_help="Apply a Task to all matching repositories of a remote Git host.",
)
@click.option("--config", help="Path to configuration file.", default="", type=str)
@click.argument("task_file", nargs=-1)
def run(config: str, task_file: list[str]):
    opts = rcmt.options_from_config(config)
    opts.task_paths = task_file
    result = rcmt.execute(opts)
    if result is False:
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
    opts = rcmt.options_from_config(config)
    opts.task_paths = [task_file]
    log_level = logging.getLevelName(opts.config.log_level.upper())
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
    )
    rcmt.execute_verify(
        directory=directory, opts=opts, out=sys.stdout, repo_name=repository
    )


@click.command()
def version():
    click.echo(rcmt.__version__)


@click.group()
def main():
    pass


main.add_command(run)
main.add_command(verify)
main.add_command(version)
