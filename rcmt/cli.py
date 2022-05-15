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
@click.option(
    "--packages",
    help="Path to packages directory.",
    multiple=True,
    required=False,
    type=str,
)
@click.option("--repo-source", default="github.com", show_default=True, type=str)
@click.option("--repo-project", default="wndhydrnt", show_default=True, type=str)
@click.option("--repo-name", default="rcmt", show_default=True, type=str)
@click.argument("run_file")
@click.argument("directory")
def local(
    config: str,
    packages: list[str],
    repo_source: str,
    repo_project: str,
    repo_name: str,
    run_file: str,
    directory: str,
):
    opts = rcmt.options_from_config(config)
    opts.matcher_path = run_file
    opts.packages_paths = packages
    rcmt.execute_local(
        directory=directory,
        repo_source=repo_source,
        repo_project=repo_project,
        repo_name=repo_name,
        opts=opts,
    )


@click.command()
@click.option("--config", help="Path to configuration file.", default="", type=str)
@click.option(
    "--packages",
    help="Path to packages directory.",
    multiple=True,
    required=False,
    type=str,
)
@click.argument("matcher_file")
def run(config: str, packages: list[str], matcher_file: str):
    opts = rcmt.options_from_config(config)
    opts.matcher_path = matcher_file
    opts.packages_paths = packages
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
