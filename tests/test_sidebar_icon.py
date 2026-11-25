import sys
from pathlib import Path

import flet as ft
import pytest

from xl_utils.ui import assets
from xl_utils.ui.components import sidebar as sidebar_module
from xl_utils.ui.components.sidebar import Sidebar


def _logo_mark(sidebar: Sidebar) -> ft.Control:
    logo = sidebar.control.content.controls[0]
    return logo.content.controls[0]


def test_dev_assets_point_to_the_repo_icons() -> None:
    assert assets.asset_path("icon.png") is not None
    assert assets.asset_path("icon.ico") is not None
    assert assets.asset_path("nao-existe.png") is None


def test_sidebar_shows_the_real_icon() -> None:
    sidebar = Sidebar([], lambda _index: None)

    mark = _logo_mark(sidebar)

    assert isinstance(mark, ft.Image)
    assert isinstance(mark.src, bytes)
    assert mark.width == mark.height == sidebar_module.LOGO_SIZE


def test_sidebar_falls_back_to_the_x_without_the_png(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sidebar_module, "asset_path", lambda _name: None)

    sidebar = Sidebar([], lambda _index: None)

    mark = _logo_mark(sidebar)
    assert isinstance(mark, ft.Container)
    assert mark.content.value == "x"


def test_frozen_app_reads_assets_from_the_bundle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "icon.png").write_bytes(b"png")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

    assert assets.asset_path("icon.png") == tmp_path / "assets" / "icon.png"
    assert assets.asset_path("icon.ico") is None


@pytest.mark.parametrize(
    ("platform", "name"), [("win32", "icon.ico"), ("linux", "icon.png")]
)
def test_window_icon_matches_the_platform(
    monkeypatch: pytest.MonkeyPatch, platform: str, name: str
) -> None:
    monkeypatch.setattr(sys, "platform", platform)

    icon = assets.window_icon()

    assert icon is not None
    assert icon.name == name
