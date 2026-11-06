"""Paletas Dracula (escura) e clara, e o tema Flet construído a partir delas."""

import contextlib
import dataclasses

import flet as ft

DARK = {
    "BACKGROUND": "#282A36",
    "BACKGROUND_DEEP": "#21222C",
    "SURFACE": "#343746",
    "BORDER": "#44475A",
    "TEXT": "#F8F8F2",
    "MUTED": "#6272A4",
    "SUBTLE_TEXT": "#C9CBDC",
    "CHIP_TEXT": "#B8BCD0",
    "PURPLE": "#BD93F9",
    "PINK": "#FF79C6",
    "GREEN": "#50FA7B",
    "YELLOW": "#F1FA8C",
    "RED": "#FF5555",
    "CYAN": "#8BE9FD",
    "ORANGE": "#FFB86C",
    "SUCCESS_BG": "#22342A",
    "SUCCESS_BORDER": "#2C4A38",
    "ERROR_BG": "#3A2428",
    "INFO_BG": "#1F3438",
    "SELECTED_BG": "#2D2A47",
    "ICON_BG": "#332B45",
}

# Variante clara do Dracula (Alucard): creme quente, sem branco puro.
LIGHT = {
    "BACKGROUND": "#F2EEE1",
    "BACKGROUND_DEEP": "#E9E4D4",
    "SURFACE": "#FBF7E9",
    "BORDER": "#D7D0BC",
    "TEXT": "#1F1F1F",
    "MUTED": "#6C664B",
    "SUBTLE_TEXT": "#4B4636",
    "CHIP_TEXT": "#4B4636",
    "PURPLE": "#644AC9",
    "PINK": "#A3144D",
    "GREEN": "#14710A",
    "YELLOW": "#75600F",
    "RED": "#B02A1C",
    "CYAN": "#036A96",
    "ORANGE": "#A34D14",
    "SUCCESS_BG": "#E6F2DB",
    "SUCCESS_BORDER": "#A9C79A",
    "ERROR_BG": "#F8E3DD",
    "INFO_BG": "#E1EEF2",
    "SELECTED_BG": "#E7E1F5",
    "ICON_BG": "#ECE6F8",
}

PALETTES = {"dark": DARK, "light": LIGHT}
DEFAULT_MODE = "dark"

# Tokens ativos: apply() troca o conjunto antes de a UI ser montada.
globals().update(DARK)

# Menor tamanho usado na UI: dicas, contadores, logs e células da tabela.
FONT_XS = 12
FONT_SM = 13
FONT_MD = 15
FONT_TITLE = 24
FONT_HERO = 26


def apply(mode: str) -> str:
    """Ativa a paleta de ``mode`` e devolve o modo efetivo (escuro no fallback)."""
    active = mode if mode in PALETTES else DEFAULT_MODE
    globals().update(PALETTES[active])
    return active


# Campos que carregam cor numa cor ou num estilo do Flet.
_COLOR_FIELDS = frozenset(
    {
        "active_color",
        "active_track_color",
        "bgcolor",
        "border_color",
        "check_color",
        "color",
        "colors",
        "cursor_color",
        "divider_color",
        "fill_color",
        "focus_color",
        "focused_border_color",
        "heading_row_color",
        "hover_color",
        "icon_color",
        "inactive_color",
        "inactive_track_color",
        "indicator_color",
        "overlay_color",
        "selection_color",
        "shadow_color",
        "surface_tint_color",
        "thumb_color",
        "track_color",
    }
)

# Nunca percorrer dados de aplicação: um log pode conter um hex como texto.
_SKIP_FIELDS = frozenset({"data", "key"})

# Só descemos por controles e estilos; medidas, alinhamentos e enums ficam de fora.
_NODE_TYPES = (
    ft.Control,
    ft.Gradient,
    ft.TextStyle,
    ft.ButtonStyle,
    ft.Border,
    ft.BorderSide,
)


def color_mapping(old_mode: str, new_mode: str) -> dict[str, str]:
    """Mapeia as cores da paleta antiga para os tokens da nova."""
    old = PALETTES.get(old_mode, DARK)
    new = PALETTES.get(new_mode, DARK)
    return {old[token].upper(): new[token] for token in old}


def restyle(control: object, mapping: dict[str, str]) -> None:
    """Recolore a árvore já montada, preservando estado, textos e estrutura."""
    _restyle_value(control, mapping, {})


def _restyle_value(
    value: object,
    mapping: dict[str, str],
    memo: dict[int, object],
    *,
    is_color: bool = False,
) -> object:
    if isinstance(value, str):
        return mapping.get(value.upper(), value) if is_color else value
    if isinstance(value, (bool, int, float, bytes)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        items = [
            _restyle_value(item, mapping, memo, is_color=is_color) for item in value
        ]
        return tuple(items) if isinstance(value, tuple) else items
    if isinstance(value, dict):
        for key, item in value.items():
            value[key] = _restyle_value(item, mapping, memo)
        return value
    if not isinstance(value, _NODE_TYPES):
        return value

    identity = id(value)
    if identity in memo:
        return memo[identity]
    # Guarda contra ciclos enquanto a subárvore ainda está sendo percorrida.
    memo[identity] = value

    fields = getattr(type(value), "__dataclass_fields__", None)
    if not fields:
        return value

    updates: dict[str, object] = {}
    for name in fields:
        if name.startswith("_") or name in _SKIP_FIELDS:
            continue
        current = getattr(value, name, None)
        updated = _restyle_value(
            current,
            mapping,
            memo,
            is_color=name in _COLOR_FIELDS,
        )
        if updated is not current:
            updates[name] = updated

    if not updates:
        return value

    if isinstance(value, ft.Control):
        for name, updated in updates.items():
            with contextlib.suppress(AttributeError, TypeError):
                setattr(value, name, updated)
        return value

    # Tipos de valor (Border, BorderSide, TextStyle, ButtonStyle, Gradient) são
    # trocados inteiros. Mutar BorderSide no lugar faz o Flet mandar um patch
    # parcial e o Container perde o border_radius ao vivo.
    with contextlib.suppress(TypeError):
        rebuilt = dataclasses.replace(value, **updates)
        memo[identity] = rebuilt
        return rebuilt
    return value


def build_theme(mode: str = DEFAULT_MODE) -> ft.Theme:
    """Devolve o tema Flet da paleta pedida."""
    palette = PALETTES.get(mode, DARK)
    return ft.Theme(
        use_material3=True,
        color_scheme=ft.ColorScheme(
            primary=palette["PURPLE"],
            on_primary=palette["BACKGROUND_DEEP"],
            secondary=palette["PINK"],
            on_secondary=palette["BACKGROUND_DEEP"],
            surface=palette["SURFACE"],
            on_surface=palette["TEXT"],
            surface_container=palette["BACKGROUND"],
            surface_container_high=palette["SURFACE"],
            surface_container_highest=palette["BORDER"],
            outline=palette["BORDER"],
            outline_variant=palette["BORDER"],
            error=palette["RED"],
            on_error=palette["BACKGROUND_DEEP"],
        ),
    )
