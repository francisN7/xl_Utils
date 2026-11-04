import asyncio
import threading
from pathlib import Path

import flet as ft

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

    def handler(
        state: ToolState,
        result: ResultPanel,
        progress,
    ) -> None:
        handler_threads.append(threading.current_thread())
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
    assert all(thread is threading.main_thread() for thread in update_threads)
    assert layout.result.status == "Concluído"
    assert not layout.state.running
    assert not layout._running
    assert "1 de 1 arquivo(s) concluído(s)" in " ".join(_texts(layout.result.control))
