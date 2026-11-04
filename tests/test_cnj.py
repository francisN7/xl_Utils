from pathlib import Path

import pandas as pd
import pytest

from xl_utils.controllers.cnj import run_cnj
from xl_utils.core.io import read_workbook
from xl_utils.core.save import save_chosen, save_to_output
from xl_utils.core.tools.cnj import (
    collect_cnjs,
    count_cnjs,
    extract_cnjs,
    normalize_cnj,
)

FIRST = "0001234-56.2024.8.26.0100"
FIRST_DIGITS = "00012345620248260100"
SECOND = "0009999-99.2024.8.26.0100"


def test_extract_cnjs_finds_both_formats_in_a_sentence() -> None:
    text = f"Processo {FIRST}, protocolo {FIRST_DIGITS}."

    assert extract_cnjs(text) == [FIRST, FIRST_DIGITS]


def test_extract_cnjs_ignores_longer_numbers_and_cpf() -> None:
    assert extract_cnjs("123456789012345678901") == []
    assert extract_cnjs("CPF 123.456.789-00") == []


def test_normalize_cnj_accepts_both_formats() -> None:
    assert normalize_cnj(FIRST) == FIRST
    assert normalize_cnj(FIRST_DIGITS) == FIRST


@pytest.mark.parametrize("value", ["", "123", "abc", FIRST + "0"])
def test_normalize_cnj_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError, match="CNJ inválido"):
        normalize_cnj(value)


def test_collect_cnjs_deduplicates_across_sheets() -> None:
    sheets = {
        "Uma": pd.DataFrame({"texto": [f"{FIRST} e {FIRST_DIGITS}", SECOND, None]}),
        "Outra": pd.DataFrame({"processo": [FIRST, "sem cnj"]}),
    }

    assert collect_cnjs(sheets) == [FIRST, SECOND]
    assert count_cnjs(sheets) == 4


def test_collect_cnjs_reads_duplicate_column_names() -> None:
    frame = pd.DataFrame([[FIRST, SECOND]], columns=["processo", "processo"])

    assert collect_cnjs({"Uma": frame}) == [FIRST, SECOND]


def test_run_cnj_prepares_a_sorted_unique_list(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    with pd.ExcelWriter(source) as writer:
        pd.DataFrame({"texto": [f"{FIRST} e {FIRST_DIGITS}", SECOND]}).to_excel(
            writer, sheet_name="Uma", index=False
        )
        pd.DataFrame({"processo": [FIRST]}).to_excel(
            writer,
            sheet_name="Outra",
            index=False,
        )

    outcome = run_cnj(source)

    assert not (tmp_path / "output").exists()
    assert outcome.item.output_dir == tmp_path / "output"
    assert outcome.suggested_name == "entrada lista cnj.xlsx"
    assert outcome.cnjs == [FIRST, SECOND]
    assert outcome.found == 4
    assert outcome.duplicates == 2
    assert any("Duplicados removidos: 2" in line for line in outcome.log)

    saved = save_chosen([outcome.item], tmp_path / "lista.xlsx")
    assert saved is not None
    frame = read_workbook(saved[0], dtype=str)["PROCESSOS"]
    assert frame["PROCESSOS"].tolist() == [FIRST, SECOND]


def test_run_cnj_ignores_unselected_sheets(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    with pd.ExcelWriter(source) as writer:
        pd.DataFrame({"texto": [FIRST]}).to_excel(writer, sheet_name="Uma", index=False)
        pd.DataFrame({"processo": [SECOND]}).to_excel(
            writer, sheet_name="Outra", index=False
        )

    outcome = run_cnj(source, selected={"Uma"})

    assert outcome.cnjs == [FIRST]
    assert outcome.found == 1
    assert outcome.duplicates == 0


def test_run_cnj_without_matches_prepares_an_empty_list(tmp_path: Path) -> None:
    source = tmp_path / "vazia.xlsx"
    pd.DataFrame({"texto": ["nada aqui", None]}).to_excel(
        source,
        index=False,
    )

    outcome = run_cnj(source)

    assert outcome.cnjs == []
    assert outcome.found == 0
    assert outcome.duplicates == 0
    assert not (tmp_path / "output").exists()

    saved = save_to_output([outcome.item])
    assert saved[0].is_file()
    frame = read_workbook(saved[0], dtype=str)["PROCESSOS"]
    assert list(frame.columns) == ["PROCESSOS"]
    assert frame.empty
