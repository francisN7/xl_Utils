"""Ferramenta montada a partir do manifesto do plugin, sem Flet no plugin."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path

import flet as ft

from xl_utils import __version__
from xl_utils.controllers.plugins import PluginOutcome, execute_plugin
from xl_utils.core.paths import default_output_dir, safe_file_part
from xl_utils.core.plugins.manifest import MAX_TEXT_LENGTH, OptionSpec
from xl_utils.core.plugins.page import OptionError, PageSpec, validate
from xl_utils.core.save import SaveItem
from xl_utils.shared.log import RunLog
from xl_utils.shared.plugins.install import InstalledPlugin
from xl_utils.shared.plugins.loader import PluginLoader
from xl_utils.shared.progress import CancelToken, NullReporter, ProgressReporter
from xl_utils.ui import theme
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.components.tool_layout import ToolLayout
from xl_utils.ui.drive import DriveSession
from xl_utils.ui.state import ToolState


def build_plugin_page(
    plugin: InstalledPlugin,
    *,
    loader: PluginLoader,
    drive: DriveSession | None = None,
    on_back: Callable[[], None] | None = None,
) -> ft.Control:
    """Monta a página declarativa e conecta o botão Executar ao plugin."""
    if plugin.manifest is None:
        return _broken(plugin, "O manifesto não foi lido; reabra a área de plugins.")
    spec = PageSpec.from_manifest(plugin.manifest)
    controls: dict[str, ft.Control] = {}
    labels = [slot.label for slot in spec.inputs]
    slots = {slot.label: slot.key for slot in spec.inputs}
    required = {slot.label for slot in spec.inputs if slot.required}

    def options(_state: ToolState, _overlay: object = None) -> ft.Control:
        return _options_panel(spec, controls)

    def ready(_state: ToolState, selected: Mapping[str, Path | None]) -> bool:
        return all(selected.get(label) is not None for label in required)

    layout = ToolLayout(
        spec.title,
        spec.description,
        options=options if spec.options else None,
        note=spec.note,
        multiple_files=spec.multiple_files,
        default_all_sheets=spec.default_all_sheets,
        inputs=labels or None,
        ready=ready if labels else None,
        run_handler=lambda state, result, progress, token: _run(
            plugin,
            loader,
            spec,
            controls,
            slots,
            state,
            result,
            progress,
            token,
        ),
        drive=drive,
    )

    parts: list[ft.Control] = []
    if on_back is not None:
        parts.append(
            ft.Container(
                content=ft.TextButton(
                    "Plugins",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda _event: on_back(),
                ),
                padding=ft.Padding.only(left=16, top=8),
            )
        )
    parts.append(layout.control)
    page = ft.Column(controls=parts, spacing=0, expand=True)
    page.data = {"layout": layout}
    return page


def _options_panel(
    spec: PageSpec,
    controls: dict[str, ft.Control],
) -> ft.Control:
    fields: list[ft.Control] = []
    for option in spec.options:
        control = _control(option)
        controls[option.key] = control
        fields.append(control)
        hint = _hint(option)
        if hint:
            fields.append(
                ft.Text(hint, size=theme.FONT_XS, color=theme.MUTED),
            )
    return ft.Column(controls=fields, spacing=8)


def _control(option: OptionSpec) -> ft.Control:
    if option.kind == "text":
        return ft.TextField(
            label=option.label,
            value=str(option.default),
            max_length=MAX_TEXT_LENGTH,
            dense=True,
            text_size=theme.FONT_SM,
            label_style=ft.TextStyle(size=theme.FONT_XS),
        )
    if option.kind == "int":
        return ft.TextField(
            label=option.label,
            value=str(option.default),
            input_filter=ft.NumbersOnlyInputFilter(),
            keyboard_type=ft.KeyboardType.NUMBER,
            dense=True,
            text_size=theme.FONT_SM,
            label_style=ft.TextStyle(size=theme.FONT_XS),
        )
    if option.kind == "bool":
        return ft.Checkbox(
            label=option.label,
            value=bool(option.default),
            label_style=ft.TextStyle(size=theme.FONT_SM),
        )
    return ft.Dropdown(
        label=option.label,
        value=str(option.default),
        options=[
            ft.DropdownOption(key=choice, text=choice) for choice in option.choices
        ],
        dense=True,
        text_size=theme.FONT_SM,
        label_style=ft.TextStyle(size=theme.FONT_XS),
    )


def _hint(option: OptionSpec) -> str:
    if option.help:
        return option.help
    if option.kind == "int" and (option.min is not None or option.max is not None):
        low = "—" if option.min is None else str(option.min)
        high = "—" if option.max is None else str(option.max)
        return f"De {low} a {high}."
    return ""


def _run(
    plugin: InstalledPlugin,
    loader: PluginLoader,
    spec: PageSpec,
    controls: Mapping[str, ft.Control],
    slots: Mapping[str, str],
    state: ToolState,
    result: ResultPanel,
    progress: ProgressReporter | NullReporter,
    token: CancelToken,
) -> None:
    options = _collect(spec, controls)
    inputs = {
        slots[label]: path for label, path in state.inputs.items() if label in slots
    }
    sheets = {path: tuple(names) for path, names in state.selected_sheets.items()}
    outcome = execute_plugin(
        plugin,
        loader=loader,
        files=tuple(state.files),
        inputs=inputs,
        sheets=sheets,
        options=options,
        log=state.log or RunLog(),
        progress=progress,
        token=token,
        app_version=__version__,
    )
    _show(plugin, spec, state, result, outcome, token)


def _collect(
    spec: PageSpec,
    controls: Mapping[str, ft.Control],
) -> dict[str, str | int | bool]:
    values: dict[str, object] = {}
    for option in spec.options:
        control = controls.get(option.key)
        values[option.key] = getattr(control, "value", None)
    try:
        return validate(spec, values)
    except OptionError as error:
        raise ValueError(str(error)) from error


def _show(
    plugin: InstalledPlugin,
    spec: PageSpec,
    state: ToolState,
    result: ResultPanel,
    outcome: PluginOutcome,
    token: CancelToken,
) -> None:
    items = _save_items(plugin, spec, state, outcome)
    if token.cancelled:
        result.set_cancelled(
            outcome.frames or None,
            "Execução cancelada",
            outcome.message,
        )
        return
    if not outcome.frames:
        result.set_info(
            spec.title,
            outcome.message or "O plugin não devolveu tabelas.",
        )
        return
    state.result = dict(outcome.frames)
    state.save_items = items
    state.message = outcome.message
    detail = outcome.message or f"{len(outcome.frames)} tabela(s) pronta(s)"
    result.set_ready(outcome.frames, f"{spec.title} concluído", detail)


def _save_items(
    plugin: InstalledPlugin,
    spec: PageSpec,
    state: ToolState,
    outcome: PluginOutcome,
) -> list[SaveItem]:
    """Usa os itens do plugin ou monta um livro único a partir dos frames."""
    if outcome.save_items:
        return list(outcome.save_items)
    if not outcome.frames:
        return []
    sources = list(state.files) or list(state.inputs.values())
    output_dir = default_output_dir(sources[0]) if sources else Path.cwd() / "output"
    name = f"{safe_file_part(spec.title)}_{plugin.version}.xlsx"
    return [
        SaveItem(
            suggested_name=name,
            sheets=dict(outcome.frames),
            output_dir=output_dir,
        )
    ]


def _broken(plugin: InstalledPlugin, detail: str) -> ft.Control:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(plugin.name, size=theme.FONT_TITLE, weight=ft.FontWeight.BOLD),
                ft.Text(detail, size=theme.FONT_SM, color=theme.RED),
            ],
            spacing=8,
        ),
        padding=24,
        expand=True,
    )


__all__ = ["build_plugin_page"]
