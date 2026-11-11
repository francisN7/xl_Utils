"""Os exemplos publicados nos docs empacotam e executam de verdade."""

from __future__ import annotations

from pathlib import Path

from xl_utils import __version__
from xl_utils.controllers.plugins import execute_plugin
from xl_utils.core.plugins.manifest import PluginManifest, parse_manifest
from xl_utils.core.plugins.package import build_package, inspect_package, verify_sidecar
from xl_utils.core.plugins.page import PageSpec, validate
from xl_utils.shared.log import RunLog
from xl_utils.shared.plugins.install import InstalledPlugin, install_package
from xl_utils.shared.plugins.loader import PluginLoader
from xl_utils.shared.progress import CancelToken, NullReporter

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "plugins" / "exemplos"


def manifest_of(name: str) -> PluginManifest:
    return parse_manifest((EXAMPLES / name / "plugin.toml").read_bytes())


def install_example(name: str, tmp_path: Path) -> InstalledPlugin:
    archive = build_package(EXAMPLES / name, tmp_path / f"{name}.tar.xz")
    verify_sidecar(archive)
    inspect_package(archive, app_version=__version__)
    return install_package(
        archive,
        root=tmp_path / "plugins",
        app_version=__version__,
    )


def execute(
    plugin: InstalledPlugin,
    *,
    files=(),
    inputs=None,
    sheets=None,
    options=None,
):
    return execute_plugin(
        plugin,
        loader=PluginLoader(),
        files=files,
        inputs=inputs or {},
        sheets=sheets or {},
        options=options or {},
        log=RunLog(),
        progress=NullReporter(),
        token=CancelToken(),
        app_version=__version__,
    )


def test_examples_have_stable_ids() -> None:
    assert manifest_of("hello").id == "exemplo.hello"
    assert manifest_of("com-opcoes").id == "exemplo.com-opcoes"


def test_hello_counts_each_selected_sheet(tmp_path: Path, xlsx_file: Path) -> None:
    plugin = install_example("hello", tmp_path)

    outcome = execute(
        plugin,
        files=(xlsx_file,),
        sheets={xlsx_file: ("Dados",)},
    )

    frame = outcome.frames["resumo"]
    assert list(frame.columns) == ["arquivo", "aba", "linhas"]
    assert frame.iloc[0]["aba"] == "Dados"
    assert frame.iloc[0]["linhas"] == 3
    assert outcome.message == "1 aba(s) lida(s)"


def test_com_opcoes_uses_named_slots_and_typed_options(
    tmp_path: Path,
    xlsx_file: Path,
) -> None:
    plugin = install_example("com-opcoes", tmp_path)
    options = validate(
        PageSpec.from_manifest(manifest_of("com-opcoes")),
        {"limite": "2", "modo": "colunas"},
    )

    outcome = execute(
        plugin,
        inputs={"origem": xlsx_file},
        sheets={xlsx_file: ("Dados",)},
        options=options,
    )

    frame = outcome.frames["resumo"]
    assert frame.iloc[0]["titulo"] == "Resumo"
    assert frame.iloc[0]["aba"] == "Dados"
    assert "codigo" in str(frame.iloc[0]["resultado"])
    assert outcome.message == "Resumo: 1 aba(s)"


def test_com_opcoes_requires_the_origin(tmp_path: Path) -> None:
    plugin = install_example("com-opcoes", tmp_path)
    options = validate(PageSpec.from_manifest(manifest_of("com-opcoes")), {})

    outcome = execute(plugin, options=options)

    assert outcome.frames == {}
    assert "origem" in outcome.message


def test_examples_package_only_the_manifest_and_lib(tmp_path: Path) -> None:
    for name in ("hello", "com-opcoes"):
        archive = build_package(EXAMPLES / name, tmp_path / f"{name}.tar.xz")
        info = inspect_package(archive)

        names = {entry.name for entry in info.entries}
        assert "plugin.toml" in names
        assert all(
            entry.startswith("lib/") for entry in names if entry != "plugin.toml"
        )
