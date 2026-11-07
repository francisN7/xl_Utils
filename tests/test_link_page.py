from pathlib import Path

from xl_utils.ui.pages.link import LinkOptions, _hint, _ready
from xl_utils.ui.state import ToolState


def _files(**values: Path | None) -> dict[str, Path | None]:
    files: dict[str, Path | None] = {
        "AGENDA": None,
        "PROCESSOS": None,
        "FINANCEIRO": None,
        "CLIENTES": None,
    }
    files.update(values)
    return files


def test_ready_needs_at_least_one_flow(tmp_path: Path) -> None:
    state = ToolState()
    processos = tmp_path / "processos.xlsx"

    assert not _ready(state, _files(PROCESSOS=processos))
    assert _hint(state, _files(PROCESSOS=processos)) == (
        "Anexe a AGENDA e/ou o FINANCEIRO."
    )


def test_ready_agenda_requires_processos(tmp_path: Path) -> None:
    state = ToolState()
    agenda = tmp_path / "agenda.xlsx"
    processos = tmp_path / "processos.xlsx"

    assert not _ready(state, _files(AGENDA=agenda))
    assert _hint(state, _files(AGENDA=agenda)) == "AGENDA: falta PROCESSOS"
    assert _ready(state, _files(AGENDA=agenda, PROCESSOS=processos))
    assert _hint(state, _files(AGENDA=agenda, PROCESSOS=processos)) is None


def test_ready_financeiro_accepts_processos_or_clientes(tmp_path: Path) -> None:
    state = ToolState()
    financeiro = tmp_path / "financeiro.xlsx"
    processos = tmp_path / "processos.xlsx"
    clientes = tmp_path / "clientes.xlsx"

    assert not _ready(state, _files(FINANCEIRO=financeiro))
    assert _hint(state, _files(FINANCEIRO=financeiro)) == (
        "FINANCEIRO: falta PROCESSOS ou CLIENTES"
    )
    assert _ready(state, _files(FINANCEIRO=financeiro, PROCESSOS=processos))
    assert _ready(state, _files(FINANCEIRO=financeiro, CLIENTES=clientes))


def test_ready_blocks_the_whole_run_when_agenda_lacks_processos(
    tmp_path: Path,
) -> None:
    state = ToolState()
    agenda = tmp_path / "agenda.xlsx"
    financeiro = tmp_path / "financeiro.xlsx"
    clientes = tmp_path / "clientes.xlsx"

    files = _files(AGENDA=agenda, FINANCEIRO=financeiro, CLIENTES=clientes)
    assert not _ready(state, files)
    assert _hint(state, files) == "AGENDA: falta PROCESSOS"


def test_ready_blocks_repeated_files(tmp_path: Path) -> None:
    state = ToolState()
    agenda = tmp_path / "agenda.xlsx"

    files = _files(AGENDA=agenda, PROCESSOS=agenda)
    assert not _ready(state, files)
    assert _hint(state, files) == "Selecione arquivos diferentes em cada campo."


def test_link_options_start_unchecked_and_follow_the_inputs(tmp_path: Path) -> None:
    state = ToolState()
    options = LinkOptions(state, lambda: None)

    assert state.options["name_in_description"].value is False
    assert state.options["name_in_description"].disabled
    assert state.options["single_field_agenda"].disabled
    assert state.options["single_field_financeiro"].disabled

    state.inputs = {"AGENDA": tmp_path / "agenda.xlsx"}
    options.refresh()
    assert not state.options["single_field_agenda"].disabled
    assert state.options["single_field_financeiro"].disabled

    state.inputs = {
        "FINANCEIRO": tmp_path / "financeiro.xlsx",
        "PROCESSOS": tmp_path / "processos.xlsx",
    }
    options.refresh()
    assert not state.options["name_in_description"].disabled
    assert not state.options["single_field_financeiro"].disabled
