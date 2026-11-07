import asyncio
import threading
from pathlib import Path

import flet as ft

from xl_utils.shared.progress import ProgressEvent
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.components.tool_layout import ToolLayout
from xl_utils.ui.state import ToolState


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


def test_layout_without_options_hides_the_options_card() -> None:
    layout = ToolLayout(
        "Sem opções",
        "Teste",
        note="Comportamento fixo.",
    )

    texts = _texts(layout.control)

    assert "1. Entrada" in texts
    assert "2. Resultado" in texts
    assert "2. Opções" not in texts
    assert "3. Resultado" not in texts
    assert texts.count("Comportamento fixo.") == 1


def test_layout_with_options_keeps_the_options_card() -> None:
    layout = ToolLayout(
        "Com opções",
        "Teste",
        options=ft.Text("Campo editável"),
    )
    texts = _texts(layout.control)

    assert "2. Opções" in texts
    assert "3. Resultado" in texts


def test_run_handler_leaves_the_ui_thread(xlsx_file: Path, monkeypatch) -> None:
    handler_threads: list[threading.Thread] = []
    tokens = []

    def handler(
        state: ToolState,
        result: ResultPanel,
        progress,
        token,
    ) -> None:
        handler_threads.append(threading.current_thread())
        tokens.append(token)
        progress.file_started(state.files[0].name)
        progress.file_done(state.files[0].name)
        result.set_ready({}, "Concluído")

    layout = ToolLayout("Execução", "Teste", run_handler=handler)
    layout.state.select_files([xlsx_file])

    update_threads: list[threading.Thread] = []
    original_update = layout.result._update_now

    def record_update() -> None:
        update_threads.append(threading.current_thread())
        original_update()

    monkeypatch.setattr(layout.result, "_update_now", record_update)

    class FakePage:
        def run_task(self, callback) -> None:
            asyncio.run(callback())

    monkeypatch.setattr(layout, "_page", lambda: FakePage())
    layout._run()

    assert handler_threads
    assert handler_threads[0] is not threading.main_thread()
    assert tokens == [layout._token]
    assert all(thread is threading.main_thread() for thread in update_threads)
    assert layout.result.status == "Concluído"
    assert not layout.state.running
    assert not layout._running
    assert "1 de 1 arquivo(s) concluído(s)" in " ".join(_texts(layout.result.control))


def test_labeled_inputs_require_all_entries(
    xlsx_file: Path,
    tmp_path: Path,
) -> None:
    agenda = tmp_path / "agenda.xlsx"
    processos = tmp_path / "processos.xlsx"
    agenda.write_bytes(xlsx_file.read_bytes())
    processos.write_bytes(xlsx_file.read_bytes())

    layout = ToolLayout("Vinculação", "Teste", inputs=("AGENDA", "PROCESSOS"))
    layout._file_inputs["AGENDA"].set_files([agenda])

    assert layout._run_button.disabled
    assert layout.state.inputs == {"AGENDA": agenda}

    layout._file_inputs["PROCESSOS"].set_files([processos])

    assert not layout._run_button.disabled
    assert layout.state.inputs == {"AGENDA": agenda, "PROCESSOS": processos}
    texts = _texts(layout.control)
    assert "AGENDA" in texts
    assert "PROCESSOS" in texts
    assert "Abas" not in texts


def test_custom_ready_and_hint_drive_the_button(
    xlsx_file: Path,
    tmp_path: Path,
) -> None:
    agenda = tmp_path / "agenda.xlsx"
    processos = tmp_path / "processos.xlsx"
    agenda.write_bytes(xlsx_file.read_bytes())
    processos.write_bytes(xlsx_file.read_bytes())

    def ready(_state: ToolState, files: dict[str, Path | None]) -> bool:
        return files.get("AGENDA") is not None and files.get("PROCESSOS") is not None

    def hint(_state: ToolState, files: dict[str, Path | None]) -> str | None:
        if files.get("AGENDA") is not None and files.get("PROCESSOS") is None:
            return "AGENDA: falta PROCESSOS"
        return None

    layout = ToolLayout(
        "Fluxo",
        "Teste",
        inputs=("AGENDA", "PROCESSOS"),
        ready=ready,
        hint=hint,
    )
    layout._file_inputs["AGENDA"].set_files([agenda])

    assert layout._run_button.disabled
    assert layout._summary.value == "AGENDA: falta PROCESSOS"

    layout._file_inputs["PROCESSOS"].set_files([processos])

    assert not layout._run_button.disabled
    assert layout._summary.value == "AGENDA: agenda.xlsx · PROCESSOS: processos.xlsx"


def test_execute_button_becomes_cancel_while_running(xlsx_file: Path) -> None:
    layout = ToolLayout(
        "Cancelamento",
        "Teste",
        run_handler=lambda *_args: None,
    )
    layout.state.select_files([xlsx_file])

    layout._begin([])

    assert layout._cancel_button.visible
    assert not layout._run_button.visible
    assert not layout._cancel_button.disabled

    layout._cancel_clicked()

    assert layout._token is not None
    assert layout._token.cancelled
    assert layout._cancel_button.disabled

    layout._finish()

    assert layout._run_button.visible
    assert not layout._cancel_button.visible
    assert not layout._run_button.disabled


def test_progress_stage_updates_text_and_log_immediately() -> None:
    panel = ResultPanel()
    panel.set_running("Executando")
    panel.start_progress(1)

    panel.apply_progress(
        ProgressEvent(kind="stage", total=1, completed=0, line="Lendo planilha")
    )

    texts = _texts(panel.control)
    assert "Lendo planilha" in texts
    assert "[INFO] Lendo planilha" in texts
    assert panel._progress_bar.value is None


def test_progress_bar_is_indeterminate_while_a_file_runs() -> None:
    panel = ResultPanel()
    panel.set_running("Executando")
    panel.start_progress(2)

    panel.apply_progress(
        ProgressEvent(kind="file_started", total=2, completed=0, index=1, name="a")
    )
    assert panel._progress_bar.value is None

    panel.apply_progress(
        ProgressEvent(kind="file_done", total=2, completed=1, name="a")
    )
    assert panel._progress_bar.value == 0.5
