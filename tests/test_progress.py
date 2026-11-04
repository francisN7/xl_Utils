from xl_utils.shared.progress import NullReporter, ProgressEvent, ProgressReporter


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
