import click

from xl_Utils.commands import extract_cnj


@click.group()
@click.version_option(prog_name="xl_Utils")
def xrun() -> None:
    pass


xrun.add_command(extract_cnj)
