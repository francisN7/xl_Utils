"""CLI de desenvolvimento de plugins: empacotar, conferir, instalar e remover.

Uso:
  uv run python scripts/plugin_cli.py pack <pasta> -o <pacote.tar.xz>
  uv run python scripts/plugin_cli.py check <pacote.tar.xz>
  uv run python scripts/plugin_cli.py install <pacote.tar.xz>
  uv run python scripts/plugin_cli.py list
  uv run python scripts/plugin_cli.py uninstall <id>

Não executa código do plugin. O entry point do instalador continua sendo a UI.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from xl_utils import __version__
from xl_utils.core.plugins import PluginError
from xl_utils.core.plugins.package import build_package, inspect_package, verify_sidecar
from xl_utils.shared.plugins.install import (
    install_package,
    scan_installed,
    uninstall_plugin,
)


def build_parser() -> argparse.ArgumentParser:
    """Monta o parser dos subcomandos."""
    parser = argparse.ArgumentParser(
        prog="plugin_cli",
        description="Ferramenta de desenvolvimento de plugins do xl_Utils.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    pack = commands.add_parser("pack", help="Empacota uma pasta em .tar.xz.")
    pack.add_argument("source", type=Path, help="Pasta com plugin.toml e lib/.")
    pack.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Arquivo de saída .tar.xz.",
    )

    check = commands.add_parser(
        "check",
        help="Confere sidecar, manifesto, caminhos e limites.",
    )
    check.add_argument("archive", type=Path, help="Pacote .tar.xz.")

    install = commands.add_parser("install", help="Instala um pacote validado.")
    install.add_argument("archive", type=Path, help="Pacote .tar.xz.")

    list_cmd = commands.add_parser("list", help="Lista plugins instalados.")
    list_cmd.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Raiz alternativa (testes e desenvolvimento).",
    )

    uninstall = commands.add_parser("uninstall", help="Remove um plugin.")
    uninstall.add_argument("id", help="ID do plugin, como autor.ferramenta.")
    uninstall.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Raiz alternativa (testes e desenvolvimento).",
    )

    install.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Raiz alternativa (testes e desenvolvimento).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Executa o subcomando e devolve o código de saída."""
    args = build_parser().parse_args(argv)
    try:
        match args.command:
            case "pack":
                _pack(args.source, args.output)
            case "check":
                _check(args.archive)
            case "install":
                _install(args.archive, args.root)
            case "list":
                _list(args.root)
            case "uninstall":
                _uninstall(args.id, args.root)
            case _:
                return 2
    except PluginError as error:
        print(f"ERRO [{error.code}] {error}", file=sys.stderr)
        return 1
    return 0


def _pack(source: Path, output: Path) -> None:
    package = build_package(source, output)
    print(f"Pacote: {package}")
    print(f"Sidecar: {package.with_name(package.name + '.sha256')}")


def _check(archive: Path) -> None:
    info = inspect_package(archive, app_version=__version__)
    digest = verify_sidecar(archive)
    manifest = info.manifest
    print(f"ID: {manifest.id}")
    print(f"Nome: {manifest.name}")
    print(f"Versão: {manifest.version} (API {manifest.api_version})")
    print(f"Entrypoint: {manifest.entrypoint}")
    print(f"Entradas: {len(info.entries)}")
    print(f"Extraído: {info.total_size} bytes")
    print(f"Pacote: {info.archive_size} bytes")
    print(f"SHA-256: {digest}")


def _install(archive: Path, root: Path | None) -> None:
    plugin = install_package(archive, root=root)
    print(f"Instalado: {plugin.id} {plugin.version}")
    print(f"Pasta: {plugin.path}")


def _list(root: Path | None) -> None:
    result = scan_installed(root=root)
    if not result.valid and not result.invalid:
        print("Nenhum plugin instalado.")
        return
    for plugin in result.valid:
        print(
            f"{plugin.id}\t{plugin.version}\tAPI {plugin.api_version}\t"
            f"{plugin.name}\t{plugin.path}"
        )
    for invalid in result.invalid:
        print(f"INVÁLIDO [{invalid.code}] {invalid.path}: {invalid.message}")


def _uninstall(plugin_id: str, root: Path | None) -> None:
    uninstall_plugin(plugin_id, root=root)
    print(f"Removido: {plugin_id}")


if __name__ == "__main__":
    raise SystemExit(main())
