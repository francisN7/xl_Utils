"""Resultado acima do limite de linhas sai em vários arquivos."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from xl_utils.core import save
from xl_utils.core.io import read_workbook
from xl_utils.core.save import SaveItem, save_chosen, save_to_output, split_item


def _item(tmp_path: Path, rows: int, extra: int = 0) -> SaveItem:
    sheets = {"Mesclado": pd.DataFrame({"n": [str(i) for i in range(rows)]})}
    if extra:
        sheets["Resumo"] = pd.DataFrame({"x": ["a"] * extra})
    return SaveItem("Merge.xlsx", sheets, tmp_path / "output")


def test_default_limit_is_one_million() -> None:
    assert save.ROW_LIMIT == 1_000_000


def test_item_within_the_limit_stays_whole(tmp_path: Path) -> None:
    item = _item(tmp_path, 5)

    assert split_item(item, 5) == [item]


def test_item_over_the_limit_is_split_in_parts(tmp_path: Path) -> None:
    parts = split_item(_item(tmp_path, 7, extra=2), 3)

    assert [part.suggested_name for part in parts] == [
        "Merge_parte1.xlsx",
        "Merge_parte2.xlsx",
        "Merge_parte3.xlsx",
    ]
    assert [len(part.sheets["Mesclado"]) for part in parts] == [3, 3, 1]
    assert list(parts[0].sheets) == ["Mesclado", "Resumo"]
    assert list(parts[1].sheets) == ["Mesclado"]
    assert parts[2].sheets["Mesclado"]["n"].tolist() == ["6"]


@pytest.fixture
def small_limit(monkeypatch) -> None:
    monkeypatch.setattr(save, "ROW_LIMIT", 3)


@pytest.mark.usefixtures("small_limit")
def test_save_to_output_writes_one_file_per_part(tmp_path: Path) -> None:
    paths = save_to_output([_item(tmp_path, 7)])

    assert [path.name for path in paths] == [
        "Merge_parte1.xlsx",
        "Merge_parte2.xlsx",
        "Merge_parte3.xlsx",
    ]
    rows = [
        next(iter(read_workbook(path, dtype=str).values()))["n"].tolist()
        for path in paths
    ]
    assert rows == [["0", "1", "2"], ["3", "4", "5"], ["6"]]


@pytest.mark.usefixtures("small_limit")
def test_chosen_file_name_is_kept_in_the_parts(tmp_path: Path) -> None:
    paths = save_chosen([_item(tmp_path, 4)], tmp_path / "escolhido.xlsx")

    assert [path.name for path in paths] == [
        "escolhido_parte1.xlsx",
        "escolhido_parte2.xlsx",
    ]
