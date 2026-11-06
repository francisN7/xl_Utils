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


def test_sidebar_button_saves_and_asks_for_a_restart() -> None:
    changes: list[str] = []
    sidebar = Sidebar(
        [],
        lambda _index: None,
        theme_mode="dark",
        on_theme_change=changes.append,
    )

    assert sidebar._theme_button.content == "Tema claro"
    assert sidebar._theme_button.icon == ft.Icons.LIGHT_MODE

    sidebar._toggle_theme()

    assert changes == ["light"]
    assert sidebar._theme_button.content == "Tema escuro"
    assert sidebar._theme_button.icon == ft.Icons.DARK_MODE
    assert sidebar._theme_hint.visible is True


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


class _FakeSidebar:
    instances: list[_FakeSidebar] = []

    def __init__(
        self,
        _tools: object,
        _on_select: object,
        *,
        selected: int = 0,
        theme_mode: str = "dark",
        on_theme_change: object = None,
    ) -> None:
        self.control = ft.Container()
        self.theme_mode = theme_mode
        self.on_theme_change = on_theme_change
        self.background_at_build = theme.BACKGROUND
        self.selected = selected
        self.__class__.instances.append(self)

    def select(self, index: int) -> None:
        self.selected = index


def test_main_applies_the_saved_theme_before_building_the_sidebar(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _FakeSidebar.instances = []
    saved: list[str] = []

    monkeypatch.setattr(settings, "load_theme", lambda: "light")
    monkeypatch.setattr(settings, "save_theme", saved.append)
    monkeypatch.setattr(app, "Sidebar", _FakeSidebar)
    monkeypatch.setattr(app, "build_home", lambda _on_open: ft.Container())
    monkeypatch.setattr(ft.Container, "update", lambda _self: None)

    page = _FakePage()
    app.main(page)

    sidebar = _FakeSidebar.instances[0]
    assert page.theme_mode == ft.ThemeMode.LIGHT
    assert sidebar.background_at_build == theme.LIGHT["BACKGROUND"]
    assert sidebar.theme_mode == "light"

    sidebar.on_theme_change("light")
    assert saved == ["light"]
