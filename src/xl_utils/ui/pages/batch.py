"""Helpers for tools that process several files in one run."""

from collections.abc import Callable, Collection, Sequence
from pathlib import Path
from typing import Protocol

import pandas as pd

from xl_utils.shared.log import RunLog
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.state import ToolState

Pending = list[tuple[Path, Collection[str] | None]]


class Outcome(Protocol):
    """Structure shared by the per-tool outcome dataclasses."""

    source: Path
    log: RunLog


def pending_files(state: ToolState, result: ResultPanel) -> Pending | None:
    """Return the files to run, or warn when a file has no sheet selected."""
    pending: Pending = []
    for source in state.files:
        selected = state.selected_sheets.get(source)
        if selected is not None and not selected:
            result.set_info(
                "Selecione ao menos uma aba",
                f"Marque uma aba de {source.name} antes de executar.",
            )
            return None
        pending.append((source, selected))
    return pending


def join_logs(outcomes: Sequence[Outcome]) -> RunLog:
    """Concatenate per-file logs, keeping one blank line between files."""
    log = RunLog()
    for outcome in outcomes:
        if log:
            log.info("")
        log.extend(outcome.log)
    return log


def append_outcomes(state: ToolState, outcomes: Sequence[Outcome]) -> None:
    """Append the outcome logs to the run log stored in the state."""
    log = state.log or RunLog()
    log.extend(join_logs(outcomes))
    state.log = log


def prefixed_frames(
    outcomes: Sequence[Outcome],
    frames_of: Callable[[Outcome], dict[str, pd.DataFrame]],
) -> dict[str, pd.DataFrame]:
    """Key preview frames by file when several files run together."""
    if len(outcomes) == 1:
        return frames_of(outcomes[0])
    return {
        f"{outcome.source.stem} · {name}": frame
        for outcome in outcomes
        for name, frame in frames_of(outcome).items()
    }
