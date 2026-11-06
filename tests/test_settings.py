import json
from pathlib import Path

import pytest

from xl_utils.shared import settings


def test_theme_survives_a_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"

    settings.save_theme("light", path)

    assert settings.load_theme(path) == "light"
    assert not path.with_name("settings.json.tmp").exists()


def test_missing_file_falls_back_to_dark(tmp_path: Path) -> None:
    assert settings.load_theme(tmp_path / "settings.json") == "dark"


def test_corrupted_json_falls_back_to_dark(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text("{", encoding="utf-8")

    assert settings.load_theme(path) == "dark"


def test_json_that_is_not_an_object_falls_back_to_dark(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(json.dumps(["light"]), encoding="utf-8")

    assert settings.load_theme(path) == "dark"


def test_unknown_theme_falls_back_to_dark(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"theme": "sepia"}), encoding="utf-8")

    assert settings.load_theme(path) == "dark"


def test_save_preserves_other_keys(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"zoom": 1.2}), encoding="utf-8")

    settings.save_theme("light", path)

    assert json.loads(path.read_text(encoding="utf-8")) == {
        "theme": "light",
        "zoom": 1.2,
    }


def test_save_overwrites_corrupted_json(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text("{", encoding="utf-8")

    settings.save_theme("light", path)

    assert settings.load_theme(path) == "light"


def test_invalid_mode_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        settings.save_theme("sepia", tmp_path / "settings.json")


def test_settings_path_uses_local_appdata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    assert settings.settings_path() == tmp_path / "xl_utils" / "settings.json"


def test_settings_path_falls_back_to_the_home_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda _cls: tmp_path))

    assert settings.settings_path() == tmp_path / ".xl_utils" / "settings.json"
