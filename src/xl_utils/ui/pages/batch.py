"""Auxiliares para ferramentas que processam vários arquivos numa execução."""

from collections.abc import Callable, Collection, Sequence
from pathlib import Path
from typing import Protocol

import pandas as pd

from xl_utils.shared.log import RunLog
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.state import ToolState

Pending = list[tuple[Path, Collection[str] | None]]


class Outcome(Protocol):
    """Estrutura comum aos dataclasses de resultado de cada ferramenta."""

    source: Path
    log: RunLog


def pending_files(state: ToolState, result: ResultPanel) -> Pending | None:
    """Devolve os arquivos a rodar, ou avisa quando um arquivo não tem aba."""
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
    """Concatena os logs por arquivo, com uma linha em branco entre arquivos."""
    log = RunLog()
    for outcome in outcomes:
        if log:
            log.info("")
        log.extend(outcome.log)
    return log


def append_outcomes(state: ToolState, outcomes: Sequence[Outcome]) -> None:
    """Acrescenta os logs dos resultados ao log de execução do estado."""
    log = state.log or RunLog()
    log.extend(join_logs(outcomes))
    state.log = log


def report_cancelled(
    state: ToolState,
    result: ResultPanel,
    frames: dict[str, pd.DataFrame],
    processed: int,
    total: int,
) -> None:
    """Mantém o que já foi calculado e fecha sem liberar a gravação."""
    log = state.log or RunLog()
    log.warning(f"Cancelado: {processed} de {total} arquivo(s) processado(s)")
    state.log = log
    state.result = frames or None
    state.save_items.clear()
    state.message = f"Cancelado após {processed} de {total} arquivo(s)"
    result.set_cancelled(
        frames,
        "Execução cancelada",
        f"{processed} de {total} arquivo(s) processado(s) · nada foi gravado",
    )


def prefixed_frames(
    outcomes: Sequence[Outcome],
    frames_of: Callable[[Outcome], dict[str, pd.DataFrame]],
) -> dict[str, pd.DataFrame]:
    """Identifica a prévia pelo arquivo quando vários rodam juntos."""
    if len(outcomes) == 1:
        return frames_of(outcomes[0])
    return {
        f"{outcome.source.stem} · {name}": frame
        for outcome in outcomes
        for name, frame in frames_of(outcome).items()
    }
