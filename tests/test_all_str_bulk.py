from pathlib import Path

import pandas as pd
import pytest

from xl_utils.controllers.all_str import run_all_str
from xl_utils.core.io import read_workbook
from xl_utils.core.save import save_chosen

ROWS = 1000
CITIES = (
    "São Paulo",
    "Rio de Janeiro",
    "Belo Horizonte",
    "Curitiba",
    "Recife",
)


def _build_frame() -> pd.DataFrame:
    """Build 1k fictitious rows in memory; nothing is written to the repo."""
    rows = [
        {
            "id": f"{number:06d}",
            # Ano 0000 deixa explícito que a numeração não é um CNJ real.
            "cnj": f"{number:07d}-{number % 100:02d}.0000.0.00.{number % 10000:04d}",
            "nome": f"Pessoa Fictícia {number} 🙂",
            "observacao": f"Linha {number}\nsegunda linha ✅",
            "valor": f"{number * 37 % 1_000_000:06d}",
            "cidade": CITIES[number % len(CITIES)],
            "email": f"pessoa{number}@exemplo.test",
        }
        for number in range(1, ROWS + 1)
    ]
    return pd.DataFrame(rows)


def _write_source(tmp_path: Path, frame: pd.DataFrame, suffix: str) -> Path:
    source = tmp_path / f"base_ficticia_1k{suffix}"
    if suffix == ".csv":
        frame.to_csv(source, index=False)
    else:
        frame.to_excel(source, index=False)
    return source


@pytest.mark.parametrize("suffix", [".csv", ".xlsx"])
def test_pipeline_end_to_end_with_one_thousand_rows(
    tmp_path: Path,
    suffix: str,
) -> None:
    expected = _build_frame()
    source = _write_source(tmp_path, expected, suffix)
    before = source.read_bytes()

    outcome = run_all_str(source)

    assert source.read_bytes() == before
    assert not (tmp_path / "output").exists()
    assert outcome.rows == ROWS

    saved = save_chosen([outcome.item], tmp_path / "saida.xlsx")
    assert saved is not None
    assert saved[0].suffix == ".xlsx"
    frame = next(iter(read_workbook(saved[0], dtype=str).values()))
    assert len(frame) == ROWS
    assert frame["id"].tolist() == expected["id"].tolist()
    assert frame["cnj"].tolist() == expected["cnj"].tolist()
    assert frame["valor"].tolist() == expected["valor"].tolist()
    assert frame["cidade"].tolist() == expected["cidade"].tolist()
    assert frame["email"].tolist() == expected["email"].tolist()

    assert not frame["nome"].str.contains("🙂", regex=False).any()
    assert not frame["observacao"].str.contains("✅", regex=False).any()
    assert (
        frame["nome"].tolist()
        == expected["nome"].str.replace("🙂", "", regex=False).tolist()
    )
    assert (
        frame["observacao"].tolist()
        == expected["observacao"].str.replace("✅", "", regex=False).tolist()
    )
