"""Atalho para o CLI instalado como ``xl-utils-plugin``.

Mantém o roteiro ``uv run python scripts/plugin_cli.py ...`` funcionando dentro
do repositório do app; a implementação vive em ``xl_utils.plugin_cli``.
"""

from __future__ import annotations

from xl_utils.plugin_cli import main

if __name__ == "__main__":
    raise SystemExit(main())
