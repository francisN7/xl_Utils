from pathlib import Path

import pandas as pd
import pytest

from xl_utils.controllers.all_str import run_all_str
from xl_utils.core.io import read_workbook
from xl_utils.core.save import save_chosen, save_to_output
from xl_utils.core.tools.all_str import WorkbookReadError, prepare_workbook


def test_prepare_workbook_keeps_text_and_removes_emojis(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    pd.DataFrame(
        {
            "codigo": ["000123"],
            "cnj": ["0001234-56.2024.8.26.0100"],
            "nome": ["Ana 🙂\nSilva 🚀"],
        }
    ).to_excel(source, index=False)

    frame = prepare_workbook(source)["Sheet1"]

    assert frame["codigo"].tolist() == ["000123"]
    assert frame["cnj"].tolist() == ["0001234-56.2024.8.26.0100"]
    assert frame["nome"].tolist() == ["Ana \nSilva "]


def test_prepare_workbook_cleans_every_sheet(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    with pd.ExcelWriter(source) as writer:
        pd.DataFrame({"nome": ["Ana ✅"]}).to_excel(
            writer,
            sheet_name="Uma",
            index=False,
        )
        pd.DataFrame({"nome": ["Bia ❌"]}).to_excel(
            writer,
            sheet_name="Outra",
            index=False,
        )

    sheets = prepare_workbook(source)

    assert list(sheets) == ["Uma", "Outra"]
    assert sheets["Uma"]["nome"].tolist() == ["Ana "]
    assert sheets["Outra"]["nome"].tolist() == ["Bia "]


def test_prepare_workbook_reads_csv_encoding(tmp_path: Path) -> None:
    source = tmp_path / "entrada.csv"
    source.write_bytes("nome;cidade\nJoão;São Paulo\n".encode("latin-1"))

    frame = prepare_workbook(source)["Planilha1"]

    assert frame["nome"].tolist() == ["João"]
    assert frame["cidade"].tolist() == ["São Paulo"]


def test_prepare_workbook_raises_typed_error_for_corrupt_file(
    tmp_path: Path,
) -> None:
    source = tmp_path / "quebrada.xlsx"
    source.write_bytes(b"isto nao e um xlsx")

    with pytest.raises(WorkbookReadError, match="Não foi possível ler"):
        prepare_workbook(source)


def test_run_all_str_keeps_only_the_selected_sheets(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    with pd.ExcelWriter(source) as writer:
        pd.DataFrame({"nome": ["Ana"]}).to_excel(writer, sheet_name="Uma", index=False)
        pd.DataFrame({"nome": ["Bia"]}).to_excel(
            writer, sheet_name="Outra", index=False
        )

    outcome = run_all_str(source, selected={"Outra"})

    assert list(outcome.sheets) == ["Outra"]
    assert not (tmp_path / "output").exists()
    saved = save_chosen([outcome.item], tmp_path / "escolhido.xlsx")
    assert saved is not None
    assert list(read_workbook(saved[0], dtype=str)) == ["Outra"]


def test_run_all_str_rejects_an_empty_selection(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    pd.DataFrame({"nome": ["Ana"]}).to_excel(source, index=False)

    with pytest.raises(ValueError, match="ao menos uma aba"):
        run_all_str(source, selected=set())


def test_run_all_str_prepares_the_output_folder(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    pd.DataFrame({"codigo": ["000123"], "nome": ["Ana 🙂"]}).to_excel(
        source,
        index=False,
    )

    outcome = run_all_str(source)

    assert not (tmp_path / "output").exists()
    assert outcome.item.output_dir == tmp_path / "output"
    assert outcome.suggested_name == "entrada.xlsx"
    assert outcome.rows == 1
    assert any("Pronto para salvar" in line for line in outcome.log)

    saved = save_to_output([outcome.item])
    assert saved[0].parent == tmp_path / "output"
    assert saved[0].is_file()

    frame = read_workbook(saved[0], dtype=str)["Sheet1"]
    assert frame["codigo"].tolist() == ["000123"]
    assert frame["nome"].tolist() == ["Ana "]
