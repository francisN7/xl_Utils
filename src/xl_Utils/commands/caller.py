from pathlib import Path

import click
import pandas as pd

from xl_Utils.core import CnjProcessor
from xl_Utils.utils import FileReader, save


def read(one_file: bool = False) -> dict[Path, dict[str, pd.DataFrame]]:
    reader = FileReader()
    return reader.run(one_file)


@click.command()
def extract_cnj() -> None:
    processor = CnjProcessor(read(True))
    save(processor.run())
