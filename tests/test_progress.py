from xl_utils.shared.progress import (
    CancelToken,
    NullReporter,
    ProgressEvent,
    ProgressReporter,
)
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.pages.all_str import run as run_all_str_page
from xl_utils.ui.state import ToolState


def test_reporter_counts_files_and_emits_text_without_cell_data() -> None:
    events: list[ProgressEvent] = []
    reporter = ProgressReporter(events.append)

    reporter.start(2)
    reporter.file_started("a.xlsx")
    reporter.file_done("a.xlsx")
    reporter.file_started("b.xlsx")
    reporter.file_done("b.xlsx")
    reporter.finish()

    assert [event.kind for event in events] == [
        "start",
        "file_started",
        "file_done",
        "file_started",
        "file_done",
        "finish",
    ]
    assert events[1].index == 1
    assert events[1].text == "Arquivo 1 de 2: a.xlsx"
    assert events[2].text == "Arquivo 1 de 2 concluído(s)"
    assert events[3].index == 2
    assert events[4].completed == 2
    assert events[-1].value == 1.0


def test_reporter_never_completes_more_than_the_total() -> None:
    events: list[ProgressEvent] = []
    reporter = ProgressReporter(events.append)

    reporter.start(1)
    reporter.file_done()
    reporter.file_done()
    reporter.finish()

    assert reporter.completed == 1
    assert events[-1].completed == 1
    assert events[-1].value == 1.0


def test_null_reporter_ignores_every_marker() -> None:
    reporter = NullReporter()

    reporter.start(2)
    reporter.file_started("a.xlsx")
    reporter.file_done("a.xlsx")
    reporter.finish()


def test_failing_callback_is_isolated_and_reported() -> None:
    warnings: list[str] = []

    def fail(_event: ProgressEvent) -> None:
        raise RuntimeError("loop fechado")

    reporter = ProgressReporter(fail, on_error=warnings.append)

    reporter.start(1)
    reporter.finish()

    assert warnings
    assert all("loop fechado" in warning for warning in warnings)


def test_cancel_token_starts_clear_and_sticks() -> None:
    token = CancelToken()

    assert not token.cancelled

    token.cancel()

    assert token.cancelled


def test_reporter_streams_log_lines_in_order() -> None:
    events: list[ProgressEvent] = []
    reporter = ProgressReporter(events.append)

    reporter.start(1)
    reporter.log(["[INFO] a.xlsx: 2 abas", ""])
    reporter.finish()

    assert [event.kind for event in events] == ["start", "log", "log", "finish"]
    assert events[1].text == "[INFO] a.xlsx: 2 abas"
    assert events[2].text == ""
    assert events[1].value == 0.0


def test_null_reporter_ignores_log_lines() -> None:
    reporter = NullReporter()

    reporter.log(["[INFO] ignorado"])


def test_page_cancels_between_files_and_keeps_partial_log(
    xlsx_file,
    csv_file,
) -> None:
    token = CancelToken()
    events: list[ProgressEvent] = []

    def emit(event: ProgressEvent) -> None:
        events.append(event)
        if event.kind == "file_done":
            token.cancel()

    state = ToolState(files=[xlsx_file, csv_file])
    panel = ResultPanel()

    run_all_str_page(state, panel, ProgressReporter(emit), token)

    assert token.cancelled
    assert panel.kind == "cancelled"
    assert state.save_items == []
    assert state.result
    assert [event.name for event in events if event.kind == "file_started"] == [
        xlsx_file.name
    ]
    assert any(event.kind == "log" for event in events)
    assert state.log is not None
    assert "Cancelado: 1 de 2" in state.log.to_text()
    assert not (xlsx_file.parent / "output").exists()
