import click

import rcmt


@click.command()
@click.option("--config", help="Path to configuration file.", default="", type=str)
@click.option("--packages", help="Path to packages directory.", required=True, type=str)
@click.argument("matcher")
def run(config: str, packages: str, matcher: str):
    opts = rcmt.options_from_config(config)
    opts.config.run_path = matcher
    opts.config.packages_path = packages
    rcmt.run(opts)


@click.group()
def main():
    pass


main.add_command(run)
