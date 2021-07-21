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
@click.argument("matcher")
def run(config: str, packages: list[str], matcher: str):
    opts = rcmt.options_from_config(config)
    opts.matcher_path = matcher
    opts.packages_paths = packages
    rcmt.run(opts)


@click.command()
def version():
    click.echo(rcmt.__version__)


@click.group()
def main():
    pass


main.add_command(run)
main.add_command(version)
