import click

import rcmt

local_help = """Apply a Run to a local directory.

This command allows testing of a Run and its Actions quickly. It does not clone a
repository or pushes changes to a remote.

Example Usage:

rcmt local --config <config file> <Run file> <checkout of repository>
"""


@click.command(help=local_help, short_help="Apply a Run to a local directory.")
@click.option("--config", help="Path to configuration file.", default="", type=str)
@click.option("--repo-source", default="github.com", show_default=True, type=str)
@click.option("--repo-project", default="wndhydrnt", show_default=True, type=str)
@click.option("--repo-name", default="rcmt", show_default=True, type=str)
@click.argument("run_file")
@click.argument("directory")
def local(
    config: str,
    repo_source: str,
    repo_project: str,
    repo_name: str,
    run_file: str,
    directory: str,
):
    opts = rcmt.options_from_config(config)
    opts.run_paths = [run_file]
    rcmt.execute_local(
        directory=directory,
        repo_source=repo_source,
        repo_project=repo_project,
        repo_name=repo_name,
        opts=opts,
    )


@click.command()
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
