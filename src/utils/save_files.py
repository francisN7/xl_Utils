from pathlib import Path

import pandas as pd


def save(dfs: dict[Path, dict[str, pd.DataFrame]]) -> None:
    output_folder = next(iter(dfs))
    print(output_folder)
