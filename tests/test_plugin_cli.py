"""Fluxo ponta a ponta do CLI de autoria."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from plugin_helpers import MAIN_PY, VALID_MANIFEST

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "plugin_cli.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_pack_check_install_list_uninstall(tmp_path: Path) -> None:
    source = tmp_path / "source"
    (source / "lib").mkdir(parents=True)
    (source / "plugin.toml").write_text(VALID_MANIFEST, encoding="utf-8")
    (source / "lib" / "main.py").write_text(MAIN_PY, encoding="utf-8")
    package = tmp_path / "plugin.tar.xz"

    packed = run_cli("pack", str(source), "-o", str(package))
    assert packed.returncode == 0, packed.stderr
    assert package.is_file()
    assert package.with_name(f"{package.name}.sha256").is_file()

    checked = run_cli("check", str(package))
    assert checked.returncode == 0, checked.stderr
    assert "autor.teste" in checked.stdout
    assert "SHA-256:" in checked.stdout

    root = tmp_path / "plugins"
    installed = run_cli("install", str(package), "--root", str(root))
    assert installed.returncode == 0, installed.stderr
    assert (root / "autor.teste" / "plugin.toml").is_file()

    listed = run_cli("list", "--root", str(root))
    assert listed.returncode == 0, listed.stderr
    assert "autor.teste" in listed.stdout

    removed = run_cli("uninstall", "autor.teste", "--root", str(root))
    assert removed.returncode == 0, removed.stderr
    assert not (root / "autor.teste").exists()


def test_cli_check_reports_missing_sidecar(tmp_path: Path) -> None:
    source = tmp_path / "source"
    (source / "lib").mkdir(parents=True)
    (source / "plugin.toml").write_text(VALID_MANIFEST, encoding="utf-8")
    (source / "lib" / "main.py").write_text(MAIN_PY, encoding="utf-8")
    package = tmp_path / "plugin.tar.xz"
    assert run_cli("pack", str(source), "-o", str(package)).returncode == 0
    package.with_name(f"{package.name}.sha256").unlink()

    checked = run_cli("check", str(package))
    assert checked.returncode == 1
    assert "digest_missing" in checked.stderr
