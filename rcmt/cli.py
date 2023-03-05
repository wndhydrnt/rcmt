import click

import rcmt

local_help = """Apply a Task to a local directory.

This command allows testing of a Task and its Actions quickly. It does not clone a
repository or pushes changes to a remote Git host.

Examples:

\b
# Apply Task "task.py" to a local checkout at "~/checkouts/example-repository"
rcmt local --config ./config.yaml ./task.py ~/checkouts/example-repository

\b
# Apply Task "task.py" and set a repository for templating
rcmt local --config ./config.yaml --repository github.com/wndhydrnt/rcmt ./task.py ~/checkouts/example-repository
"""


@click.command(help=local_help, short_help="Apply a Task to a local directory.")
@click.option("--config", help="Path to configuration file.", default="", type=str)
@click.option(
    "--repository",
    help="Name of the repository, e.g. github.com/wndhydrnt/rcmt. Used for templating.",
    default="",
    type=str,
)
@click.argument("task_file")
@click.argument("directory")
def local(
    config: str,
    repository: str,
    task_file: str,
    directory: str,
):
    opts = rcmt.options_from_config(config)
    opts.task_paths = [task_file]
    rcmt.execute_local(directory=directory, repository=repository, opts=opts)


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


@click.command()
def version():
    click.echo(rcmt.__version__)


@click.group()
def main():
    pass


main.add_command(local)
main.add_command(run)
main.add_command(version)
