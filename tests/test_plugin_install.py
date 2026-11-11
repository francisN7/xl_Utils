"""Instalação atômica, descoberta e desinstalação de plugins."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import time
from pathlib import Path

import pytest
from plugin_helpers import MAIN_PY, VALID_MANIFEST, valid_package, write_sidecar

from xl_utils.core.plugins.errors import InstallError, PackageError, PluginError
from xl_utils.core.plugins.package import PackageLimits
from xl_utils.shared.plugins import install as install_module
from xl_utils.shared.plugins.install import (
    install_package,
    list_installed,
    scan_installed,
    uninstall_plugin,
)


def installable(
    tmp_path: Path,
    *,
    manifest: str = VALID_MANIFEST,
    extra: dict[str, bytes] | None = None,
    sidecar: bool = True,
) -> Path:
    package = valid_package(
        tmp_path / "plugin.tar.xz",
        manifest=manifest,
        extra=extra,
    )
    if sidecar:
        write_sidecar(package)
    return package


def manifest_with_dependency() -> str:
    return VALID_MANIFEST.replace(
        'authors = ["Teste"]',
        'authors = ["Teste"]\ndependencies = ["pacote_inexistente_xyz"]',
    )


def manifest_with_min_app() -> str:
    return VALID_MANIFEST.replace(
        'authors = ["Teste"]',
        'authors = ["Teste"]\nmin_app_version = "99.0.0"',
    )


def test_install_list_and_uninstall(tmp_path: Path) -> None:
    package = installable(tmp_path)
    root = tmp_path / "plugins"
    plugin = install_package(package, root=root)

    assert plugin.id == "autor.teste"
    assert (plugin.path / "plugin.toml").is_file()
    assert (plugin.path / "lib" / "main.py").is_file()
    assert plugin.data_dir.is_dir()
    assert not (root / ".staging").exists()

    record = json.loads((plugin.path / "install.json").read_text(encoding="utf-8"))
    assert record["id"] == "autor.teste"
    assert record["version"] == "1.0.0"
    assert record["api_version"] == 1
    assert record["source"] == package.name
    assert len(record["sha256"]) == 64

    result = scan_installed(root=root)
    assert [item.id for item in result.valid] == ["autor.teste"]
    assert result.invalid == ()
    assert list_installed(root=root) == (plugin,)

    uninstall_plugin("autor.teste", root=root)
    assert not plugin.path.exists()
    assert list_installed(root=root) == ()


def test_duplicate_does_not_overwrite(tmp_path: Path) -> None:
    package = installable(tmp_path)
    root = tmp_path / "plugins"
    plugin = install_package(package, root=root)
    marker = plugin.path / "lib" / "main.py"
    marker.write_text("# preservado\n", encoding="utf-8")

    with pytest.raises(InstallError) as error:
        install_package(package, root=root)
    assert error.value.code == "plugin_duplicate"
    assert marker.read_text(encoding="utf-8") == "# preservado\n"


def test_missing_sidecar(tmp_path: Path) -> None:
    package = installable(tmp_path, sidecar=False)
    with pytest.raises(PackageError) as error:
        install_package(package, root=tmp_path / "plugins")
    assert error.value.code == "digest_missing"


def test_wrong_hash(tmp_path: Path) -> None:
    package = installable(tmp_path, sidecar=False)
    write_sidecar(package, digest="0" * 64)
    with pytest.raises(PackageError) as error:
        install_package(package, root=tmp_path / "plugins")
    assert error.value.code == "digest_invalid"


def test_missing_dependency(tmp_path: Path) -> None:
    package = installable(tmp_path, manifest=manifest_with_dependency())
    with pytest.raises(InstallError) as error:
        install_package(package, root=tmp_path / "plugins")
    assert error.value.code == "missing_dependency"


def test_app_too_old(tmp_path: Path) -> None:
    package = installable(tmp_path, manifest=manifest_with_min_app())
    with pytest.raises(PluginError) as error:
        install_package(package, root=tmp_path / "plugins")
    assert error.value.code == "app_too_old"


def test_install_enforces_final_path_length(tmp_path: Path) -> None:
    package = installable(tmp_path)
    with pytest.raises(PackageError) as error:
        install_package(
            package,
            root=tmp_path / "plugins",
            limits=PackageLimits(max_path_length=10),
        )
    assert error.value.code == "entry_unsafe"


def test_install_does_not_execute_code(tmp_path: Path) -> None:
    marker = tmp_path / "executed.txt"
    code = (
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('executou', encoding='utf-8')\n"
    )
    package = installable(
        tmp_path,
        extra={"lib/__init__.py": code.encode("utf-8")},
    )
    root = tmp_path / "plugins"
    plugin = install_package(package, root=root)
    scan_installed(root=root)
    uninstall_plugin(plugin.id, root=root)
    assert not marker.exists()


def test_malicious_package_does_not_escape(tmp_path: Path) -> None:
    sentinel = tmp_path / "escape.txt"
    sentinel.write_text("seguro", encoding="utf-8")
    package = installable(
        tmp_path,
        extra={"../escape.txt": b"invasor"},
    )
    with pytest.raises(PackageError) as error:
        install_package(package, root=tmp_path / "plugins")
    assert error.value.code in {"entry_unsafe", "entry_duplicate"}
    assert sentinel.read_text(encoding="utf-8") == "seguro"


def test_atomic_failure_leaves_no_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = installable(tmp_path)
    root = tmp_path / "plugins"

    def fail(_staging: Path, _target: Path) -> None:
        raise OSError("falha simulada")

    monkeypatch.setattr(install_module, "_promote", fail)
    with pytest.raises(InstallError) as error:
        install_package(package, root=root)
    assert error.value.code == "install_failed"
    assert not (root / "autor.teste").exists()


def test_stale_staging_is_cleaned(tmp_path: Path) -> None:
    package = installable(tmp_path)
    root = tmp_path / "plugins"
    old = root / ".staging" / "antigo"
    old.mkdir(parents=True)
    stamp = time.time() - 90_000
    os.utime(old, (stamp, stamp))

    install_package(package, root=root)
    assert not old.exists()


def test_uninstall_unknown(tmp_path: Path) -> None:
    with pytest.raises(InstallError) as error:
        uninstall_plugin("autor.inexistente", root=tmp_path / "plugins")
    assert error.value.code == "not_installed"


def test_uninstall_readonly_file(tmp_path: Path) -> None:
    package = installable(tmp_path)
    root = tmp_path / "plugins"
    plugin = install_package(package, root=root)
    protected = plugin.path / "protected.txt"
    protected.write_text("x", encoding="utf-8")
    os.chmod(protected, stat.S_IREAD)

    uninstall_plugin(plugin.id, root=root)
    assert not plugin.path.exists()


def test_uninstall_junction_does_not_follow(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    target = tmp_path / "sentinel"
    target.mkdir()
    (target / "keep.txt").write_text("keep", encoding="utf-8")
    junction = root / "autor.junction"
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(target)],
        capture_output=True,
        check=False,
    )
    if created.returncode != 0:
        pytest.skip("mklink /J indisponível neste ambiente")

    uninstall_plugin("autor.junction", root=root)
    assert not junction.exists()
    assert (target / "keep.txt").read_text(encoding="utf-8") == "keep"


def test_scan_reports_invalid(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    bad = root / "autor.ruim"
    bad.mkdir(parents=True)
    (bad / "plugin.toml").write_text("[plugin", encoding="utf-8")

    result = scan_installed(root=root)
    assert result.valid == ()
    assert len(result.invalid) == 1
    assert result.invalid[0].code == "manifest_invalid"


def test_scan_reports_missing_entrypoint(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    folder = root / "autor.teste"
    folder.mkdir(parents=True)
    (folder / "plugin.toml").write_text(VALID_MANIFEST, encoding="utf-8")

    result = scan_installed(root=root)
    assert result.valid == ()
    assert result.invalid[0].code == "entrypoint_missing"


def test_scan_reports_id_mismatch(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    folder = root / "outro.id"
    folder.mkdir(parents=True)
    (folder / "plugin.toml").write_text(VALID_MANIFEST, encoding="utf-8")

    result = scan_installed(root=root)
    assert result.valid == ()
    assert result.invalid[0].code == "invalid_id"


def test_list_empty(tmp_path: Path) -> None:
    assert list_installed(root=tmp_path / "plugins") == ()


def test_installed_files_keep_main_py(tmp_path: Path) -> None:
    package = installable(tmp_path)
    root = tmp_path / "plugins"
    plugin = install_package(package, root=root)
    assert (plugin.path / "lib" / "main.py").read_text(encoding="utf-8") == MAIN_PY
