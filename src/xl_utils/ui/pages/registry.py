"""Registry of the tool pages shown in the navigation rail."""

from collections.abc import Callable
from dataclasses import dataclass

import flet as ft

from xl_utils.ui import theme
from xl_utils.ui.components.tool_layout import ToolLayout


@dataclass(frozen=True, slots=True)
class ToolPage:
    """Metadata and factory for one tool page."""

    id: str
    label: str
    icon: ft.IconData
    description: str
    build: Callable[[], ft.Control]


def _tool(
    tool_id: str,
    label: str,
    icon: ft.IconData,
    description: str,
    options: Callable[[], ft.Control],
    *,
    multiple_files: bool = False,
) -> ToolPage:
    def build() -> ft.Control:
        return ToolLayout(
            label,
            description,
            options=options(),
            multiple_files=multiple_files,
        ).control

    return ToolPage(
        id=tool_id,
        label=label,
        icon=icon,
        description=description,
        build=build,
    )


def _check(label: str, value: bool = True) -> ft.Checkbox:
    return ft.Checkbox(label=label, value=value, disabled=True)


def _all_str_options() -> ft.Control:
    return ft.Column(
        controls=[
            _check("Remover emojis", True),
            _check("Reparar metadados se a leitura falhar", True),
            ft.Text(
                "Sempre aplicado antes das demais ferramentas.",
                size=10,
                color=theme.MUTED,
            ),
        ],
        spacing=4,
    )


def _cnj_options() -> ft.Control:
    return ft.Column(
        controls=[
            _check("Padronizar para o formato CNJ", True),
            _check("Remover duplicados", True),
        ],
        spacing=4,
    )


def _cut_options() -> ft.Control:
    return ft.Column(
        controls=[
            ft.TextField(
                label="Linhas por arquivo",
                value="1000",
                dense=True,
                disabled=True,
            ),
        ],
        spacing=8,
    )


def _merge_options() -> ft.Control:
    return ft.Column(
        controls=[
            ft.Dropdown(
                label="Modo de mesclagem",
                value="files",
                dense=True,
                disabled=True,
                options=[
                    ft.DropdownOption(
                        key="files",
                        text="Primeira aba de cada arquivo",
                    ),
                    ft.DropdownOption(
                        key="sheets",
                        text="Todas as abas de uma planilha",
                    ),
                ],
            ),
        ],
        spacing=8,
    )


TOOLS: tuple[ToolPage, ...] = (
    _tool(
        "all_str",
        "Tratamento de Texto",
        ft.Icons.TEXT_FIELDS,
        "Converte tudo para texto, remove emojis e repara metadados.",
        _all_str_options,
    ),
    _tool(
        "cnj",
        "Extrair CNJs",
        ft.Icons.SEARCH,
        "Encontra e padroniza numerações CNJ em uma planilha.",
        _cnj_options,
    ),
    _tool(
        "cut",
        "Recortar Planilha",
        ft.Icons.CONTENT_CUT,
        "Divide uma planilha em vários arquivos por quantidade de linhas.",
        _cut_options,
    ),
    _tool(
        "merge",
        "Mesclar Planilhas",
        ft.Icons.MERGE_TYPE,
        "Unifica planilhas com o mesmo cabeçalho ou as abas de uma planilha.",
        _merge_options,
        multiple_files=True,
    ),
)
