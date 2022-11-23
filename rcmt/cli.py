import click

import rcmt

local_help = """Apply a Run to a local directory.

This command allows testing of a Run and its Actions quickly. It does not clone a
repository or pushes changes to a remote Git host.

Examples:

\b
# Apply Run "run.py" to a local checkout at "~/checkouts/example-repository"
rcmt local --config ./config.yaml ./run.py ~/checkouts/example-repository

\b
# Apply Run "run.py" and set a repository for templating
rcmt local --config ./config.yaml --repository github.com/wndhydrnt/rcmt ./run.py ~/checkouts/example-repository
"""


@click.command(help=local_help, short_help="Apply a Run to a local directory.")
@click.option("--config", help="Path to configuration file.", default="", type=str)
@click.option(
    "--repository",
    help="Name of the repository, e.g. github.com/wndhydrnt/rcmt. Used for templating.",
    default="",
    type=str,
)
@click.argument("run_file")
@click.argument("directory")
def local(
    config: str,
    repository: str,
    run_file: str,
    directory: str,
):
    opts = rcmt.options_from_config(config)
    opts.run_paths = [run_file]
    rcmt.execute_local(directory=directory, repository=repository, opts=opts)


run_help = """Apply a Run to all matching repositories of a remote Git host.

rcmt will find all matching repositories, clone them, apply each Action from
the Run file and create a pull request if files have changed.

Examples:

\b
# Apply Run "run.py"
rcmt run --config ./config.yaml ./run.py
"""


@click.command(
    help=run_help,
    short_help="Apply a Run to all matching repositories of a remote Git host.",
)
@click.option("--config", help="Path to configuration file.", default="", type=str)
@click.argument("run_file", nargs=-1)
def run(config: str, run_file: list[str]):
    opts = rcmt.options_from_config(config)
    opts.run_paths = run_file
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
