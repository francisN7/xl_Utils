from pathlib import Path

import pandas as pd


def save(dfs: dict[Path, dict[str, pd.DataFrame]]) -> None:
    output_folder = next(iter(dfs)).parent.joinpath("output")
    output_folder.mkdir(exist_ok=True)
    for file in dfs.keys():
        new_file = f"{file.stem}.xlsx"
        n = 1
        while output_folder.joinpath(new_file).exists():
            new_file = f"{file.stem}_{n:03}.xlsx"
            n += 1
        with pd.ExcelWriter(output_folder.joinpath(new_file)) as writer:
            for sheet_name, df in dfs[file].items():
                df.to_excel(
                    writer, sheet_name=sheet_name, index=False, engine="xlsxwriter"
                )
