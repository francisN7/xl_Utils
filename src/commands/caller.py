from pathlib import Path

import click
import pandas as pd

from core import CnjProcessor
from utils import FileReader, save


def read(one_file: bool = False) -> dict[Path, dict[str, pd.DataFrame]]:
    reader = FileReader()
    return reader.run()


@click.command()
def extract_cnj() -> None:
    processor = CnjProcessor(read(True))
    save(processor.run())
