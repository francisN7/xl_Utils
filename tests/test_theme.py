from types import SimpleNamespace

import flet as ft
import pytest

from xl_utils import app
from xl_utils.shared import settings
from xl_utils.ui import theme
from xl_utils.ui.components.sidebar import Sidebar


@pytest.fixture(autouse=True)
def _reset_theme():
    theme.apply("dark")
    yield
    theme.apply("dark")


def _luminance(color: str) -> float:
    channels = []
    for start in (1, 3, 5):
        value = int(color[start : start + 2], 16) / 255
        channels.append(
            value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        )
    red, green, blue = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _contrast(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (_luminance(foreground), _luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def test_palettes_share_the_same_tokens() -> None:
    assert theme.DARK.keys() == theme.LIGHT.keys()


def test_light_palette_is_not_pure_white() -> None:
    assert "#FFFFFF" not in theme.LIGHT.values()
    assert theme.LIGHT["SURFACE"] != theme.LIGHT["BACKGROUND"]


def test_apply_switches_the_active_tokens() -> None:
    theme.apply("light")

    assert theme.LIGHT["BACKGROUND"] == theme.BACKGROUND
    assert theme.LIGHT["TEXT"] == theme.TEXT

    theme.apply("dark")

    assert theme.DARK["BACKGROUND"] == theme.BACKGROUND
    assert theme.DARK["TEXT"] == theme.TEXT


def test_apply_falls_back_to_dark() -> None:
    assert theme.apply("sepia") == "dark"
    assert theme.DARK["BACKGROUND"] == theme.BACKGROUND


@pytest.mark.parametrize("mode", ["dark", "light"])
def test_build_theme_uses_the_requested_palette(mode: str) -> None:
    palette = theme.PALETTES[mode]
    built = theme.build_theme(mode)

    assert built.color_scheme.primary == palette["PURPLE"]
    assert built.color_scheme.surface == palette["SURFACE"]
    assert built.color_scheme.on_surface == palette["TEXT"]
    assert built.color_scheme.outline == palette["BORDER"]


LIGHT_TEXT_PAIRS = [
    ("TEXT", "BACKGROUND"),
    ("TEXT", "BACKGROUND_DEEP"),
    ("TEXT", "SURFACE"),
    ("MUTED", "BACKGROUND"),
    ("MUTED", "BACKGROUND_DEEP"),
    ("MUTED", "SURFACE"),
    ("SUBTLE_TEXT", "BACKGROUND"),
    ("SUBTLE_TEXT", "BACKGROUND_DEEP"),
    ("SUBTLE_TEXT", "SURFACE"),
    ("CHIP_TEXT", "BACKGROUND_DEEP"),
    ("CHIP_TEXT", "SURFACE"),
    ("PURPLE", "BACKGROUND"),
    ("PURPLE", "SURFACE"),
    ("PINK", "BACKGROUND"),
    ("GREEN", "BACKGROUND"),
    ("YELLOW", "BACKGROUND"),
    ("RED", "BACKGROUND"),
    ("CYAN", "BACKGROUND"),
    ("ORANGE", "BACKGROUND"),
]


@pytest.mark.parametrize(("foreground", "background"), LIGHT_TEXT_PAIRS)
def test_light_palette_text_meets_aa(foreground: str, background: str) -> None:
    assert _contrast(theme.LIGHT[foreground], theme.LIGHT[background]) >= 4.5


@pytest.mark.parametrize("background", ["BACKGROUND", "BACKGROUND_DEEP", "SURFACE"])
def test_dark_primary_text_meets_aa(background: str) -> None:
    assert _contrast(theme.DARK["TEXT"], theme.DARK[background]) >= 4.5


def test_sidebar_button_toggles_without_a_restart_prompt() -> None:
    changes: list[str] = []
    sidebar = Sidebar(
        [],
        lambda _index: None,
        theme_mode="dark",
        on_theme_change=changes.append,
    )

    assert sidebar._theme_button.content == "Tema claro"
    assert sidebar._theme_button.icon == ft.Icons.LIGHT_MODE
    assert not hasattr(sidebar, "_theme_hint")

    sidebar._toggle_theme()

    assert changes == ["light"]
    assert sidebar._theme_button.content == "Tema escuro"
    assert sidebar._theme_button.icon == ft.Icons.DARK_MODE


def test_restyle_swaps_explicit_colors_and_keeps_the_text() -> None:
    label = ft.Text("conteúdo", color=theme.MUTED)
    log = ft.Text("#282A36", color=theme.SUBTLE_TEXT)
    button = ft.TextButton(
        "Salvar",
        style=ft.ButtonStyle(
            color=theme.SUBTLE_TEXT,
            icon_color=theme.MUTED,
        ),
    )
    card = ft.Container(
        content=ft.Column(controls=[label, log, button]),
        bgcolor=theme.SURFACE,
        border=ft.Border.all(1, theme.BORDER),
    )

    theme.restyle(card, theme.color_mapping("dark", "light"))

    assert label.color == theme.LIGHT["MUTED"]
    assert log.color == theme.LIGHT["SUBTLE_TEXT"]
    assert log.value == "#282A36"
    assert card.bgcolor == theme.LIGHT["SURFACE"]
    assert card.border.top.color == theme.LIGHT["BORDER"]
    assert button.style.color == theme.LIGHT["SUBTLE_TEXT"]
    assert button.style.icon_color == theme.LIGHT["MUTED"]


def test_restyle_rebuilds_borders_instead_of_mutating_them() -> None:
    card = ft.Container(
        bgcolor=theme.SURFACE,
        border=ft.Border.all(1, theme.BORDER),
        border_radius=12,
    )
    original_border = card.border
    original_side = original_border.top

    theme.restyle(card, theme.color_mapping("dark", "light"))

    assert card.border_radius == 12
    assert card.border is not original_border
    assert card.border.top.color == theme.LIGHT["BORDER"]
    # O Border.all compartilha o mesmo lado; a reconstrução mantém isso.
    assert card.border.top is card.border.left
    # Nada foi mutado no objeto original: o Flet recebe o campo inteiro.
    assert original_side.color == theme.DARK["BORDER"]


def _find(control: object, kind: type) -> object | None:
    if isinstance(control, kind):
        return control
    content = getattr(control, "content", None)
    if content is not None:
        found = _find(content, kind)
        if found is not None:
            return found
    for child in getattr(control, "controls", None) or []:
        found = _find(child, kind)
        if found is not None:
            return found
    return None


class _FakeWindow(SimpleNamespace):
    width = 0
    height = 0
    min_width = 0
    min_height = 0


class _FakePage:
    def __init__(self) -> None:
        self.window = _FakeWindow()
        self.added: list[ft.Control] = []
        self.updates = 0

    def add(self, *controls: ft.Control) -> None:
        self.added.extend(controls)

    def update(self, *_args: object) -> None:
        self.updates += 1


def test_main_toggles_the_theme_live(monkeypatch: pytest.MonkeyPatch) -> None:
    saved: list[str] = []

    monkeypatch.setattr(settings, "load_theme", lambda: "dark")
    monkeypatch.setattr(settings, "save_theme", saved.append)
    monkeypatch.setattr(ft.Container, "update", lambda _self: None)

    page = _FakePage()
    app.main(page)

    row = page.added[0]
    sidebar_control = row.controls[0]
    button = _find(sidebar_control, ft.TextButton)
    assert isinstance(button, ft.TextButton)

    assert page.theme_mode == ft.ThemeMode.DARK
    assert sidebar_control.bgcolor == theme.DARK["BACKGROUND_DEEP"]

    button.on_click(None)

    assert saved == ["light"]
    assert page.theme_mode == ft.ThemeMode.LIGHT
    assert page.bgcolor == theme.LIGHT["BACKGROUND"]
    assert sidebar_control.bgcolor == theme.LIGHT["BACKGROUND_DEEP"]
    assert button.content == "Tema escuro"

    button.on_click(None)

    assert saved == ["light", "dark"]
    assert page.theme_mode == ft.ThemeMode.DARK
    assert sidebar_control.bgcolor == theme.DARK["BACKGROUND_DEEP"]
    assert button.content == "Tema claro"
