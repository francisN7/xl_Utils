"""Saving only after the user's choice, without touching the origin."""

from pathlib import Path

import pandas as pd
import pytest

from xl_utils.controllers.all_str import run_all_str
from xl_utils.core.io import read_workbook
from xl_utils.core.save import SaveError, SaveItem, save_chosen, save_to_output
from xl_utils.shared.progress import CancelToken, NullReporter
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.pages.all_str import run as run_all_str_page
from xl_utils.ui.state import ToolState


def _frame() -> pd.DataFrame:
    return pd.DataFrame({"nome": ["Ana"], "codigo": ["000123"]})


def _item(
    name: str = "saida.xlsx",
    output_dir: Path | None = None,
) -> SaveItem:
    return SaveItem(
        suggested_name=name,
        sheets={"Dados": _frame()},
        output_dir=output_dir or Path("output"),
    )


def test_controller_keeps_the_result_in_memory(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    pd.DataFrame({"nome": ["Ana"]}).to_excel(source, index=False)
    before = source.read_bytes()

    outcome = run_all_str(source)

    assert source.read_bytes() == before
    assert outcome.item.suggested_name == "entrada.xlsx"
    assert outcome.item.sheets["Sheet1"]["nome"].tolist() == ["Ana"]
    assert not (tmp_path / "output").exists()


def test_save_chosen_writes_a_single_file(tmp_path: Path) -> None:
    chosen = tmp_path / "escolhido.xlsx"

    paths = save_chosen([_item()], chosen)

    assert paths == [chosen]
    assert chosen.is_file()
    assert read_workbook(chosen, dtype=str)["Dados"]["nome"].tolist() == ["Ana"]


def test_save_chosen_adds_the_extension(tmp_path: Path) -> None:
    paths = save_chosen([_item()], tmp_path / "sem_extensao")

    assert paths == [tmp_path / "sem_extensao.xlsx"]
    assert paths is not None and paths[0].is_file()


def test_save_chosen_writes_many_items_into_a_folder(tmp_path: Path) -> None:
    folder = tmp_path / "pasta"

    paths = save_chosen([_item("um.xlsx"), _item("dois.xlsx")], folder)

    assert paths == [folder / "um.xlsx", folder / "dois.xlsx"]
    assert all(path.is_file() for path in paths or [])


def test_save_chosen_rejects_a_file_for_many_items(tmp_path: Path) -> None:
    blocker = tmp_path / "bloqueio.xlsx"
    blocker.write_bytes(b"nao e pasta")

    with pytest.raises(SaveError, match="pasta"):
        save_chosen([_item("um.xlsx"), _item("dois.xlsx")], blocker)


def test_save_chosen_cancel_writes_nothing(tmp_path: Path) -> None:
    paths = save_chosen([_item()], None)

    assert paths is None
    assert list(tmp_path.iterdir()) == []


def test_save_chosen_does_not_overwrite(tmp_path: Path) -> None:
    chosen = tmp_path / "saida.xlsx"

    first = save_chosen([_item()], chosen)
    second = save_chosen([_item()], chosen)

    assert first == [chosen]
    assert second == [tmp_path / "saida_001.xlsx"]
    assert first is not None and first[0].is_file()
    assert second is not None and second[0].is_file()


def test_save_to_output_uses_each_origin_folder(tmp_path: Path) -> None:
    first_dir = tmp_path / "a" / "output"
    second_dir = tmp_path / "b" / "output"

    paths = save_to_output(
        [
            _item("um.xlsx", first_dir),
            _item("dois.xlsx", second_dir),
        ]
    )

    assert paths == [first_dir / "um.xlsx", second_dir / "dois.xlsx"]
    assert all(path.is_file() for path in paths)


def test_save_failure_is_typed_and_writes_nothing(tmp_path: Path) -> None:
    blocker = tmp_path / "bloqueio"
    blocker.write_text("não é uma pasta", encoding="utf-8")

    with pytest.raises(SaveError, match="Não foi possível salvar"):
        save_chosen([_item()], blocker / "saida.xlsx")


def test_page_run_leaves_the_result_ready_to_save(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    pd.DataFrame({"nome": ["Ana"]}).to_excel(source, index=False)
    state = ToolState(
        files=[source],
        selected_sheets={source: {"Sheet1"}},
    )
    panel = ResultPanel()

    run_all_str_page(state, panel, NullReporter(), CancelToken())

    assert panel.kind == "ready"
    assert [item.suggested_name for item in state.save_items] == ["entrada.xlsx"]
    assert state.result is not None
    assert not (tmp_path / "output").exists()
