"""Inspeção, hash, extração e empacotamento de plugins."""

from __future__ import annotations

from pathlib import Path

import pytest
from plugin_helpers import (
    MAIN_PY,
    VALID_MANIFEST,
    add_file,
    add_member,
    tar_writer,
    valid_package,
    write_sidecar,
)

from xl_utils.core.plugins.errors import ManifestError, PackageError
from xl_utils.core.plugins.package import (
    PackageLimits,
    build_package,
    extract_package,
    inspect_package,
    sha256_file,
    verify_sidecar,
)


def package_with(
    path: Path,
    entries: list[tuple[str, bytes]],
    *,
    manifest: str = VALID_MANIFEST,
) -> Path:
    with tar_writer(path) as tar:
        add_file(tar, "plugin.toml", manifest.encode("utf-8"))
        add_file(tar, "lib/main.py", MAIN_PY.encode("utf-8"))
        for name, data in entries:
            add_file(tar, name, data)
    return path


def test_valid_package_is_inspected(tmp_path: Path) -> None:
    package = valid_package(tmp_path / "plugin.tar.xz")
    info = inspect_package(package)
    assert info.manifest.id == "autor.teste"
    assert info.total_size > 0
    assert {entry.name for entry in info.entries} >= {
        "plugin.toml",
        "lib/main.py",
        "assets/logo.txt",
    }


def test_files_property_skips_directories(tmp_path: Path) -> None:
    package = valid_package(tmp_path / "plugin.tar.xz")
    info = inspect_package(package)
    assert all(not entry.is_dir for entry in info.files)


def test_sidecar_accepts_valid_hash(tmp_path: Path) -> None:
    package = valid_package(tmp_path / "plugin.tar.xz")
    expected = sha256_file(package)
    write_sidecar(package, digest=expected)
    assert verify_sidecar(package) == expected


def test_sidecar_missing(tmp_path: Path) -> None:
    package = valid_package(tmp_path / "plugin.tar.xz")
    with pytest.raises(PackageError) as error:
        verify_sidecar(package)
    assert error.value.code == "digest_missing"


def test_sidecar_wrong_hash(tmp_path: Path) -> None:
    package = valid_package(tmp_path / "plugin.tar.xz")
    write_sidecar(package, digest="0" * 64)
    with pytest.raises(PackageError) as error:
        verify_sidecar(package)
    assert error.value.code == "digest_invalid"


def test_sidecar_wrong_filename(tmp_path: Path) -> None:
    package = valid_package(tmp_path / "plugin.tar.xz")
    write_sidecar(package, filename="outro.tar.xz")
    with pytest.raises(PackageError) as error:
        verify_sidecar(package)
    assert error.value.code == "digest_invalid"


def test_sidecar_malformed(tmp_path: Path) -> None:
    package = valid_package(tmp_path / "plugin.tar.xz")
    sidecar = package.with_name(f"{package.name}.sha256")
    sidecar.write_text("sem hash\n", encoding="utf-8")
    with pytest.raises(PackageError) as error:
        verify_sidecar(package)
    assert error.value.code == "digest_invalid"


def test_archive_missing(tmp_path: Path) -> None:
    with pytest.raises(PackageError) as error:
        inspect_package(tmp_path / "nao-existe.tar.xz")
    assert error.value.code == "archive_missing"


def test_archive_type(tmp_path: Path) -> None:
    package = valid_package(tmp_path / "plugin.zip")
    with pytest.raises(PackageError) as error:
        inspect_package(package)
    assert error.value.code == "archive_type"


def test_archive_too_large(tmp_path: Path) -> None:
    package = valid_package(tmp_path / "plugin.tar.xz")
    with pytest.raises(PackageError) as error:
        inspect_package(
            package,
            limits=PackageLimits(max_archive_bytes=1),
        )
    assert error.value.code == "archive_too_large"


def test_manifest_missing(tmp_path: Path) -> None:
    package = tmp_path / "plugin.tar.xz"
    with tar_writer(package) as tar:
        add_file(tar, "lib/main.py", MAIN_PY.encode("utf-8"))
    with pytest.raises(PackageError) as error:
        inspect_package(package)
    assert error.value.code == "manifest_missing"


def test_manifest_invalid(tmp_path: Path) -> None:
    package = package_with(tmp_path / "plugin.tar.xz", [], manifest="[plugin")
    with pytest.raises(ManifestError) as error:
        inspect_package(package)
    assert error.value.code == "manifest_invalid"


def test_manifest_too_large(tmp_path: Path) -> None:
    package = package_with(
        tmp_path / "plugin.tar.xz",
        [],
        manifest="x" * (256 * 1024 + 1),
    )
    with pytest.raises(ManifestError) as error:
        inspect_package(package)
    assert error.value.code == "manifest_too_large"


def test_entrypoint_missing(tmp_path: Path) -> None:
    package = tmp_path / "plugin.tar.xz"
    with tar_writer(package) as tar:
        add_file(tar, "plugin.toml", VALID_MANIFEST.encode("utf-8"))
    with pytest.raises(PackageError) as error:
        inspect_package(package)
    assert error.value.code == "entrypoint_missing"


@pytest.mark.parametrize(
    "name",
    [
        "../evil.txt",
        "/abs.txt",
        "C:/evil.txt",
        "a\\b.txt",
        "a:b.txt",
        "CON",
        "a.",
        "a ",
        "e\u0301.txt",
        "a" * 181,
    ],
)
def test_unsafe_names_are_rejected(tmp_path: Path, name: str) -> None:
    package = package_with(tmp_path / "plugin.tar.xz", [(name, b"x")])
    with pytest.raises(PackageError) as error:
        inspect_package(package)
    assert error.value.code in {"entry_unsafe", "entry_duplicate"}


@pytest.mark.parametrize(
    "name",
    [
        "evil.py",
        "lib/evil.pyd",
        "lib/__pycache__/evil.pyc",
        "data/evil.txt",
        "install.json",
        "nested/plugin.toml",
    ],
)
def test_forbidden_content_is_rejected(tmp_path: Path, name: str) -> None:
    package = package_with(tmp_path / "plugin.tar.xz", [(name, b"x")])
    with pytest.raises(PackageError) as error:
        inspect_package(package)
    assert error.value.code in {
        "forbidden_content",
        "reserved_path",
        "manifest_nested",
    }


def test_duplicate_entries_are_rejected(tmp_path: Path) -> None:
    package = package_with(
        tmp_path / "plugin.tar.xz",
        [("assets/x.txt", b"a"), ("assets/x.txt", b"b")],
    )
    with pytest.raises(PackageError) as error:
        inspect_package(package)
    assert error.value.code == "entry_duplicate"


def test_case_collision_is_rejected(tmp_path: Path) -> None:
    package = package_with(
        tmp_path / "plugin.tar.xz",
        [("assets/A.txt", b"a"), ("assets/a.txt", b"b")],
    )
    with pytest.raises(PackageError) as error:
        inspect_package(package)
    assert error.value.code == "entry_duplicate"


@pytest.mark.parametrize("kind", ["sym", "hard", "fifo", "chr", "blk"])
def test_special_entries_are_rejected(tmp_path: Path, kind: str) -> None:
    package = tmp_path / "plugin.tar.xz"
    with tar_writer(package) as tar:
        add_file(tar, "plugin.toml", VALID_MANIFEST.encode("utf-8"))
        add_file(tar, "lib/main.py", MAIN_PY.encode("utf-8"))
        add_member(tar, "lib/special", kind=kind, linkname="../x")
    with pytest.raises(PackageError) as error:
        inspect_package(package)
    assert error.value.code == "entry_type"


def test_too_many_entries(tmp_path: Path) -> None:
    package = valid_package(tmp_path / "plugin.tar.xz")
    with pytest.raises(PackageError) as error:
        inspect_package(
            package,
            limits=PackageLimits(max_entries=2),
        )
    assert error.value.code == "too_many_entries"


def test_file_too_large(tmp_path: Path) -> None:
    package = package_with(
        tmp_path / "plugin.tar.xz",
        [("assets/big.bin", b"x" * 2048)],
    )
    with pytest.raises(PackageError) as error:
        inspect_package(
            package,
            limits=PackageLimits(max_file_bytes=1024),
        )
    assert error.value.code == "entry_too_large"


def test_total_too_large(tmp_path: Path) -> None:
    package = package_with(
        tmp_path / "plugin.tar.xz",
        [("assets/big.bin", b"x" * 2048)],
    )
    with pytest.raises(PackageError) as error:
        inspect_package(
            package,
            limits=PackageLimits(max_extracted_bytes=1024),
        )
    assert error.value.code in {"extracted_too_large", "entry_too_large"}


def test_ratio_exceeded(tmp_path: Path) -> None:
    package = package_with(
        tmp_path / "plugin.tar.xz",
        [("assets/zeros.bin", b"\0" * 200_000)],
    )
    with pytest.raises(PackageError) as error:
        inspect_package(
            package,
            limits=PackageLimits(max_ratio=2),
        )
    assert error.value.code == "ratio_exceeded"


def test_extract_valid_package(tmp_path: Path) -> None:
    package = valid_package(tmp_path / "plugin.tar.xz")
    info = inspect_package(package)
    destination = tmp_path / "out"
    extract_package(package, destination, info)
    assert (destination / "plugin.toml").is_file()
    assert (destination / "lib" / "main.py").read_text(encoding="utf-8") == MAIN_PY
    assert (destination / "assets" / "logo.txt").read_bytes() == b"logo"


def test_build_package_round_trip(tmp_path: Path) -> None:
    source = tmp_path / "source"
    (source / "lib").mkdir(parents=True)
    (source / "assets").mkdir()
    (source / "__pycache__").mkdir()
    (source / "plugin.toml").write_text(VALID_MANIFEST, encoding="utf-8")
    (source / "lib" / "main.py").write_text(MAIN_PY, encoding="utf-8")
    (source / "assets" / "logo.txt").write_bytes(b"logo")
    (source / "__pycache__" / "x.pyc").write_bytes(b"cache")

    package = build_package(source, tmp_path / "plugin.tar.xz")
    info = inspect_package(package)
    names = {entry.name for entry in info.entries}
    assert "plugin.toml" in names
    assert "lib/main.py" in names
    assert "assets/logo.txt" in names
    assert "__pycache__" not in " ".join(names)
    assert verify_sidecar(package) == sha256_file(package)


def test_build_package_is_deterministic(tmp_path: Path) -> None:
    source = tmp_path / "source"
    (source / "lib").mkdir(parents=True)
    (source / "plugin.toml").write_text(VALID_MANIFEST, encoding="utf-8")
    (source / "lib" / "main.py").write_text(MAIN_PY, encoding="utf-8")

    first = build_package(source, tmp_path / "first.tar.xz")
    second = build_package(source, tmp_path / "second.tar.xz")
    assert sha256_file(first) == sha256_file(second)


def test_build_package_rejects_native(tmp_path: Path) -> None:
    source = tmp_path / "source"
    (source / "lib").mkdir(parents=True)
    (source / "plugin.toml").write_text(VALID_MANIFEST, encoding="utf-8")
    (source / "lib" / "main.py").write_text(MAIN_PY, encoding="utf-8")
    (source / "lib" / "evil.pyd").write_bytes(b"x")
    with pytest.raises(PackageError) as error:
        build_package(source, tmp_path / "plugin.tar.xz")
    assert error.value.code == "forbidden_content"


def test_build_package_rejects_py_outside_lib(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "plugin.toml").write_text(VALID_MANIFEST, encoding="utf-8")
    (source / "main.py").write_text(MAIN_PY, encoding="utf-8")
    with pytest.raises(PackageError) as error:
        build_package(source, tmp_path / "plugin.tar.xz")
    assert error.value.code == "forbidden_content"


def test_build_package_requires_manifest(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    with pytest.raises(ManifestError) as error:
        build_package(source, tmp_path / "plugin.tar.xz")
    assert error.value.code == "manifest_missing"


def test_build_package_requires_tar_xz(tmp_path: Path) -> None:
    source = tmp_path / "source"
    (source / "lib").mkdir(parents=True)
    (source / "plugin.toml").write_text(VALID_MANIFEST, encoding="utf-8")
    (source / "lib" / "main.py").write_text(MAIN_PY, encoding="utf-8")
    with pytest.raises(PackageError) as error:
        build_package(source, tmp_path / "plugin.zip")
    assert error.value.code == "archive_type"
