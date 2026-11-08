"""Cópia temporária das planilhas do Drive: nome seguro e limpeza."""

from __future__ import annotations

from pathlib import Path

from xl_utils.shared import drive_cache


def test_store_keeps_the_real_name_and_bytes(tmp_path: Path) -> None:
    directory = drive_cache.new_session(tmp_path)

    path = drive_cache.store(directory, "AGENDA.xlsx", b"conteudo")

    assert path.name == "AGENDA.xlsx"
    assert path.read_bytes() == b"conteudo"
    assert path.parent == directory


def test_store_replaces_windows_forbidden_characters(tmp_path: Path) -> None:
    directory = drive_cache.new_session(tmp_path)

    path = drive_cache.store(directory, "CNJ:2024?.xlsx", b"x")

    assert path.name == "CNJ_2024_.xlsx"


def test_store_never_overwrites_a_name_already_used(tmp_path: Path) -> None:
    directory = drive_cache.new_session(tmp_path)
    drive_cache.store(directory, "AGENDA.xlsx", b"a")

    second = drive_cache.store(directory, "AGENDA.xlsx", b"b")

    assert second.name == "AGENDA_001.xlsx"
    assert second.read_bytes() == b"b"


def test_store_falls_back_when_the_name_is_empty(tmp_path: Path) -> None:
    directory = drive_cache.new_session(tmp_path)

    path = drive_cache.store(directory, "", b"x")

    assert path.name == "Planilha.xlsx"


def test_reset_removes_every_previous_copy(tmp_path: Path) -> None:
    directory = drive_cache.new_session(tmp_path)
    (directory / "AGENDA.xlsx").write_bytes(b"x")

    drive_cache.reset(tmp_path)

    assert not tmp_path.exists()


def test_is_cached_recognises_the_app_cache(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    cached = drive_cache.cache_root() / "sessao" / "AGENDA.xlsx"
    cached.parent.mkdir(parents=True)
    cached.write_bytes(b"x")

    assert drive_cache.is_cached(cached) is True
    assert drive_cache.is_cached(tmp_path / "outra" / "AGENDA.xlsx") is False
