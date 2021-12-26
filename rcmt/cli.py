import click

import rcmt


@click.command()
@click.option("--config", help="Path to configuration file.", default="", type=str)
@click.option(
    "--packages",
    help="Path to packages directory.",
    multiple=True,
    required=True,
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


main.add_command(run)
main.add_command(version)
