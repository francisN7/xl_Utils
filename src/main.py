import click

from commands import extract_cnj


@click.group()
def xl_run() -> None:
    # set_root_dir()
    pass


xl_run.add_command(extract_cnj)
