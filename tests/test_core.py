from pathlib import Path

import pandas as pd
import pytest

from xl_utils.core.io import read_workbook, save_workbook
from xl_utils.core.mime import resolve_suffix
from xl_utils.core.paths import unique_path
from xl_utils.core.text import remove_emojis


def test_remove_emojis_keeps_non_strings_and_line_breaks() -> None:
    assert remove_emojis(10) == 10
    assert remove_emojis("Ana 🙂\nSilva") == "Ana \nSilva"


def test_unique_path_increments(tmp_path: Path) -> None:
    first = unique_path(tmp_path, "saida")
    first.touch()

    assert unique_path(tmp_path, "saida").name == "saida_001.xlsx"


def test_resolve_suffix_uses_content_over_name(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    pd.DataFrame({"nome": ["Ana"]}).to_excel(source, index=False)
    renamed = tmp_path / "entrada.txt"
    source.rename(renamed)

    assert resolve_suffix(renamed) == ".xlsx"


def test_read_and_save_roundtrip(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    pd.DataFrame({"nome": ["Ana"], "valor": ["1"]}).to_excel(source, index=False)

    sheets = read_workbook(source, dtype=str)
    assert list(sheets) == ["Sheet1"]

    destination = save_workbook(sheets, tmp_path / "saida.xlsx")
    saved = read_workbook(destination, dtype=str)
    assert saved["Sheet1"].to_dict("list") == {
        "nome": ["Ana"],
        "valor": ["1"],
    }


def test_read_workbook_rejects_unknown_format(tmp_path: Path) -> None:
    unknown = tmp_path / "arquivo.bin"
    unknown.write_bytes(b"nao e planilha")

    with pytest.raises(ValueError, match="Formato não suportado"):
        read_workbook(unknown)


def test_save_workbook_forces_the_xlsx_suffix(tmp_path: Path) -> None:
    destination = save_workbook(
        {"Dados": pd.DataFrame({"nome": ["Ana"]})},
        tmp_path / "saida.csv",
    )

    assert destination == tmp_path / "saida.xlsx"
    assert destination.is_file()
