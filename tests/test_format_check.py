from pathlib import Path

import flet as ft
import pytest

from xl_utils.core.mime import check_format
from xl_utils.core.tools.all_str import prepare_workbook
from xl_utils.ui.components.tool_layout import ToolLayout

_RENAMES = [
    ("xlsx_file", ".xls", ".xlsx"),
    ("csv_file", ".xlsx", ".csv"),
    ("html_file", ".xlsx", ".html"),
]


def _texts(control: object) -> list[str]:
    if isinstance(control, ft.Text):
        return [str(control.value)]

    found: list[str] = []
    content = getattr(control, "content", None)
    if content is not None:
        found.extend(_texts(content))
    for child in getattr(control, "controls", None) or []:
        found.extend(_texts(child))
    return found


def _renamed(source: Path, destination: Path) -> Path:
    destination.write_bytes(source.read_bytes())
    return destination


def _unknown_file(directory: Path) -> Path:
    source = directory / "entrada.bin"
    source.write_bytes(b"\x00\x01\x02\x03" * 16)
    return source


@pytest.mark.parametrize(("fixture_name", "declared", "detected"), _RENAMES)
def test_wrong_extension_is_read_by_content(
    fixture_name: str,
    declared: str,
    detected: str,
    request: pytest.FixtureRequest,
    tmp_path: Path,
    sample_rows: dict[str, list[str]],
) -> None:
    source = request.getfixturevalue(fixture_name)
    renamed = _renamed(source, tmp_path / f"entrada{declared}")
    before = renamed.read_bytes()

    check = check_format(renamed)

    assert check.detected == detected
    assert check.declared == declared
    assert check.effective == detected
    assert check.identified
    assert check.diverges

    frame = next(iter(prepare_workbook(renamed).values()))
    assert frame["codigo"].tolist() == sample_rows["codigo"]
    assert renamed.read_bytes() == before


def test_generic_text_detection_keeps_a_supported_extension(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "entrada.csv"
    source.write_text("codigo,nome\n000123,Ana\n", encoding="utf-8")
    monkeypatch.setattr("xl_utils.core.mime.detect_suffix", lambda path: ".txt")

    check = check_format(source)

    assert check.detected == ".txt"
    assert check.effective == ".csv"
    assert check.identified
    assert not check.diverges


def test_xlsm_content_is_not_a_divergence(
    tmp_path: Path,
    xlsx_file: Path,
) -> None:
    source = tmp_path / "macro.xlsm"
    source.write_bytes(xlsx_file.read_bytes())

    check = check_format(source)

    assert check.detected == ".xlsx"
    assert check.declared == ".xlsm"
    assert check.effective == ".xlsx"
    assert not check.diverges


def test_htm_and_html_are_equivalent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "entrada.html"
    source.write_text(
        "<table><tr><th>a</th></tr><tr><td>1</td></tr></table>",
        encoding="utf-8",
    )
    monkeypatch.setattr("xl_utils.core.mime.detect_suffix", lambda path: ".htm")

    check = check_format(source)

    assert check.detected == ".htm"
    assert check.declared == ".html"
    assert not check.diverges


def test_unknown_content_and_extension_is_not_identified(tmp_path: Path) -> None:
    check = check_format(_unknown_file(tmp_path))

    assert check.detected is None
    assert check.effective == ".bin"
    assert not check.identified
    assert not check.diverges
    assert "desconhecido" in check.reason


def test_entry_shows_the_real_type_when_it_differs(
    tmp_path: Path,
    xlsx_file: Path,
) -> None:
    renamed = _renamed(xlsx_file, tmp_path / "entrada.xls")
    layout = ToolLayout("Teste", "Teste")

    layout.file_input.set_files([renamed])

    assert "conteúdo: .xlsx · nome: .xls" in _texts(layout.control)


def test_entry_stays_clean_when_the_extension_matches(xlsx_file: Path) -> None:
    layout = ToolLayout("Teste", "Teste")

    layout.file_input.set_files([xlsx_file])

    assert not any(text.startswith("conteúdo:") for text in _texts(layout.control))


def test_unidentified_format_blocks_the_run(tmp_path: Path) -> None:
    source = _unknown_file(tmp_path)
    before = source.read_bytes()
    calls: list[list[Path]] = []
    layout = ToolLayout(
        "Teste",
        "Teste",
        run_handler=lambda state, result, _progress, _token: calls.append(state.files),
    )

    layout.file_input.set_files([source])

    assert any(
        "Não foi possível identificar o formato" in text
        for text in _texts(layout.control)
    )

    layout._run()

    assert source.read_bytes() == before
    assert not calls
    assert layout.result.kind == "error"
    assert layout.result.status == "Não foi possível identificar o formato"
    assert "entrada.bin" in (layout.state.error or "")
    assert layout.state.log is not None
    assert "Formato não identificado" in layout.state.log.to_text()
    assert "Formato: não identificado" in layout.result.diagnostics


def test_divergence_is_logged_and_does_not_block(
    tmp_path: Path,
    xlsx_file: Path,
) -> None:
    renamed = _renamed(xlsx_file, tmp_path / "entrada.xls")
    before = renamed.read_bytes()
    calls: list[list[Path]] = []
    layout = ToolLayout(
        "Teste",
        "Teste",
        run_handler=lambda state, result, _progress, _token: calls.append(state.files),
    )

    layout.file_input.set_files([renamed])
    layout._run()

    assert renamed.read_bytes() == before
    assert calls
    assert layout.result.kind != "error"
    assert layout.state.log is not None
    log = layout.state.log.to_text()
    assert "[AVISO]" in log
    assert "conteúdo .xlsx" in log
    assert "Formato: conteúdo .xlsx" in layout.result.diagnostics
    assert "Divergência: conteúdo difere da extensão" in layout.result.diagnostics
