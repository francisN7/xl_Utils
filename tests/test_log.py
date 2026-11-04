from pathlib import Path

from xl_utils.shared.log import RunLog, build_diagnostics
from xl_utils.ui.state import ToolState

_VERSIONS = {
    "App": "9.9.9",
    "Python": "3.15.0",
    "pandas": "3.1.0",
    "Flet": "1.0.5",
}


def test_run_log_keeps_the_event_order_and_levels() -> None:
    log = (
        RunLog()
        .info("Arquivo: entrada.xlsx")
        .success("Saída: resultado.xlsx")
        .warning("Confira a seleção")
        .error("ValueError: vazio")
    )

    assert [event.level for event in log.events] == [
        "info",
        "success",
        "warning",
        "error",
    ]
    assert [event.text for event in log.events] == [
        "Arquivo: entrada.xlsx",
        "Saída: resultado.xlsx",
        "Confira a seleção",
        "ValueError: vazio",
    ]
    assert log.to_text().splitlines() == [
        "[INFO] Arquivo: entrada.xlsx",
        "[OK] Saída: resultado.xlsx",
        "[AVISO] Confira a seleção",
        "[ERRO] ValueError: vazio",
    ]


def test_run_log_is_list_compatible_and_supports_blank_lines() -> None:
    log = RunLog().info("um").info("")
    log.extend(["dois", "três"])

    assert list(log) == ["[INFO] um", "", "[INFO] dois", "[INFO] três"]
    assert len(log) == 4
    assert bool(log)
    assert not RunLog()


def test_diagnostics_includes_versions_files_sheets_and_options(
    tmp_path: Path,
) -> None:
    source = tmp_path / "entrada.xlsx"
    text = build_diagnostics(
        tool="Tratamento de texto",
        files=[source],
        sheets={source: ["Dados", "Outra"]},
        options={"rows_per_file": "500"},
        message="1 arquivo(s), 2 aba(s)",
        versions=_VERSIONS,
    )

    assert "Diagnóstico — xl_utils" in text
    assert "Ferramenta: Tratamento de texto" in text
    assert "  App: 9.9.9" in text
    assert "  Python: 3.15.0" in text
    assert "  pandas: 3.1.0" in text
    assert "  Flet: 1.0.5" in text
    assert str(source) in text
    assert "Abas: Dados, Outra" in text
    assert "rows_per_file: 500" in text
    assert "Resultado: 1 arquivo(s), 2 aba(s)" in text
    assert "Erro:" not in text
    assert "Traceback:" not in text


def test_diagnostics_includes_error_type_message_cause_and_traceback(
    tmp_path: Path,
) -> None:
    source = tmp_path / "quebrada.xlsx"
    try:
        try:
            raise OSError("arquivo travado")
        except OSError as cause:
            raise ValueError("não foi possível ler") from cause
    except ValueError as error:
        failure = error

    text = build_diagnostics(
        tool="Tratamento de texto",
        files=[source],
        sheets={source: []},
        error=failure,
        traceback_text="Traceback (most recent call last):\nValueError: falhou",
        versions=_VERSIONS,
    )

    assert "Erro:" in text
    assert "Tipo: ValueError" in text
    assert "Mensagem: não foi possível ler" in text
    assert "Causa: OSError: arquivo travado" in text
    assert "Traceback:" in text
    assert "ValueError: falhou" in text
    assert "Opções:" not in text
    assert "Resultado:" not in text
    # The empty sheet selection must not produce an empty "Abas:" line.
    assert "Abas:" not in text


def test_diagnostics_without_error_has_no_empty_sections() -> None:
    text = build_diagnostics(versions=_VERSIONS)

    assert "Versões:" in text
    assert "Ferramenta:" not in text
    assert "Arquivos:" not in text
    assert "Opções:" not in text
    assert "Resultado:" not in text
    assert "Erro:" not in text
    assert "Traceback:" not in text


def test_tool_state_resets_the_log_and_exposes_plain_options() -> None:
    state = ToolState(
        log=RunLog().info("antigo"),
        error_detail="traceback antigo",
        options={"rows_per_file": "500"},
    )

    assert state.diagnostic_options() == {"rows_per_file": "500"}

    state.select_files([Path("novo.xlsx")])

    assert state.log is None
    assert state.error_detail is None
