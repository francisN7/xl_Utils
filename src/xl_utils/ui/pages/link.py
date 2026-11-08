"""Ligação da página com a vinculação entre as quatro planilhas."""

from __future__ import annotations

import contextlib
from collections.abc import Callable, Mapping
from pathlib import Path

import flet as ft
import pandas as pd

from xl_utils.controllers.link import LinkOutcome, migration_warning, run_link
from xl_utils.core.tools.link import FinanceiroStats
from xl_utils.shared.progress import CancelToken, NullReporter, ProgressReporter
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.components.tool_layout import ToolLayout
from xl_utils.ui.drive import DriveSession
from xl_utils.ui.pages.batch import append_outcomes
from xl_utils.ui.state import ToolState

LABELS = ("AGENDA", "PROCESSOS", "FINANCEIRO", "CLIENTES")
DESCRIPTION = (
    "Confere os vínculos entre AGENDA, FINANCEIRO, PROCESSOS e CLIENTES; "
    "a presença do arquivo define o fluxo."
)
NOTE = (
    "A AGENDA exige PROCESSOS; o FINANCEIRO exige PROCESSOS ou CLIENTES. "
    "Com só CLIENTES, testa apenas o nome. A saída preserva colunas e abas."
)


def build(drive: DriveSession | None = None) -> ft.Control:
    """Monta a página com quatro entradas e as opções de vinculação."""

    def make_options(state: ToolState) -> LinkOptions:
        return LinkOptions(state, lambda: layout.refresh())

    layout = ToolLayout(
        "Verificar Vínculos",
        DESCRIPTION,
        note=NOTE,
        inputs=LABELS,
        options=make_options,
        ready=_ready,
        hint=_hint,
        pre_run=_pre_run,
        run_handler=run,
        drive=drive,
    )
    return layout.control


def _ready(_state: ToolState, files: Mapping[str, Path | None]) -> bool:
    """Confere a combinação de arquivos exigida por cada fluxo."""
    paths = [path.resolve() for path in files.values() if path is not None]
    if len(paths) != len(set(paths)):
        return False

    has_agenda = files.get("AGENDA") is not None
    has_financeiro = files.get("FINANCEIRO") is not None
    if not has_agenda and not has_financeiro:
        return False
    if has_agenda and files.get("PROCESSOS") is None:
        return False
    return not (
        has_financeiro
        and files.get("PROCESSOS") is None
        and files.get("CLIENTES") is None
    )


def _hint(_state: ToolState, files: Mapping[str, Path | None]) -> str | None:
    """Explica o que falta antes de liberar o botão Executar."""
    paths = [path.resolve() for path in files.values() if path is not None]
    if len(paths) != len(set(paths)):
        return "Selecione arquivos diferentes em cada campo."

    has_agenda = files.get("AGENDA") is not None
    has_financeiro = files.get("FINANCEIRO") is not None
    if not has_agenda and not has_financeiro:
        return "Anexe a AGENDA e/ou o FINANCEIRO."

    missing: list[str] = []
    if has_agenda and files.get("PROCESSOS") is None:
        missing.append("AGENDA: falta PROCESSOS")
    if (
        has_financeiro
        and files.get("PROCESSOS") is None
        and files.get("CLIENTES") is None
    ):
        missing.append("FINANCEIRO: falta PROCESSOS ou CLIENTES")
    return " · ".join(missing) if missing else None


def _pre_run(state: ToolState) -> str | None:
    """Lê só o necessário para saber se a AGENDA já foi processada."""
    agenda = state.inputs.get("AGENDA")
    if agenda is None or state.options.get("reprocess"):
        return None
    try:
        return migration_warning(agenda)
    except Exception:  # noqa: BLE001 - a execução real reporta o erro
        return None


def run(
    state: ToolState,
    result: ResultPanel,
    progress: ProgressReporter | NullReporter,
    token: CancelToken,
) -> None:
    """Executa os fluxos presentes e deixa os livros prontos para salvar."""
    del token  # a ferramenta termina em poucas leituras; não há lote para cancelar
    outcomes = run_link(
        agenda=state.inputs.get("AGENDA"),
        processos=state.inputs.get("PROCESSOS"),
        financeiro=state.inputs.get("FINANCEIRO"),
        clientes=state.inputs.get("CLIENTES"),
        allow_migrated=bool(state.options.get("reprocess")),
        name_in_description=_checked(state, "name_in_description"),
        single_field_agenda=_checked(state, "single_field_agenda"),
        single_field_financeiro=_checked(state, "single_field_financeiro"),
        progress=progress,
    )
    if not outcomes:
        result.set_info("Nada a fazer", "Anexe a AGENDA e/ou o FINANCEIRO.")
        return

    append_outcomes(state, outcomes)
    state.save_items = [outcome.item for outcome in outcomes]
    state.result = _preview(outcomes)
    state.message = " · ".join(_summary(outcome) for outcome in outcomes)
    title = "Planilhas verificadas" if len(outcomes) > 1 else "Planilha verificada"
    result.set_ready(state.result, title, state.message)


def _preview(outcomes: list[LinkOutcome]) -> dict[str, pd.DataFrame]:
    """Combina as abas transformadas, evitando nome repetido na prévia."""
    frames: dict[str, pd.DataFrame] = {}
    for outcome in outcomes:
        for name, frame in outcome.preview.items():
            key = name
            if key in frames:
                key = f"{outcome.source.stem} · {name}"
            frames[key] = frame
    return frames


def _summary(outcome: LinkOutcome) -> str:
    """Resume o fluxo da AGENDA ou do FINANCEIRO."""
    stats = outcome.stats
    if isinstance(stats, FinanceiroStats):
        numbers = (
            f"{stats.linked} vínculo(s) numérico(s)"
            if stats.numbers_tested
            else "só nomes"
        )
        return (
            f"{outcome.source.stem}: {stats.rows} linha(s) · {numbers} · "
            f"nome {stats.name_yes} SIM/{stats.name_no} NÃO"
        )
    return (
        f"{outcome.source.stem}: {stats.rows} linha(s) · "
        f"{stats.linked} vínculo(s) · {stats.unlinked} sem vínculo"
    )


def _checked(state: ToolState, key: str) -> bool:
    """Lê o valor atual de uma opção, mesmo depois de ela ser reconstruída."""
    control = state.options.get(key)
    return bool(getattr(control, "value", False))


class LinkOptions:
    """Opções que se refazem quando os arquivos anexados mudam."""

    def __init__(self, state: ToolState, on_change: Callable[[], None]) -> None:
        self._state = state
        self._on_change = on_change
        self.control = ft.Column(spacing=4)
        self.refresh()

    def refresh(self) -> None:
        """Habilita só as opções que fazem sentido para os arquivos atuais."""
        has_agenda = self._state.inputs.get("AGENDA") is not None
        has_financeiro = self._state.inputs.get("FINANCEIRO") is not None
        has_processos = self._state.inputs.get("PROCESSOS") is not None
        self.control.controls = [
            self._checkbox(
                "name_in_description",
                "Nome sem vínculo na descrição (FINANCEIRO)",
                enabled=has_financeiro,
            ),
            self._checkbox(
                "single_field_agenda",
                "Manter apenas um campo vinculante — AGENDA",
                enabled=has_agenda,
            ),
            self._checkbox(
                "single_field_financeiro",
                "Manter apenas um campo vinculante — FINANCEIRO",
                enabled=has_financeiro and has_processos,
            ),
        ]
        with contextlib.suppress(RuntimeError):
            self.control.update()

    def _checkbox(self, key: str, label: str, *, enabled: bool) -> ft.Checkbox:
        previous = self._state.options.get(key)
        value = bool(getattr(previous, "value", False)) and enabled
        checkbox = ft.Checkbox(
            label=label,
            value=value,
            disabled=not enabled,
            on_change=self._changed,
        )
        self._state.options[key] = checkbox
        return checkbox

    def _changed(self, _event=None) -> None:
        self._on_change()
