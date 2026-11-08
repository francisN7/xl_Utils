#!/usr/bin/env python
"""Teste semi-automático do Picker do Drive com a conta real.

Abre o navegador, espera a escolha e imprime só o necessário: nome, tipo e
tamanho do arquivo baixado. Nunca imprime token, código ou segredo, e não grava
conta nenhuma.

Uso:
    uv run python scripts/check-drive-picker.py
    uv run python scripts/check-drive-picker.py --multiple
    uv run python scripts/check-drive-picker.py --timeout 300
"""

from __future__ import annotations

import argparse
import sys

from xl_utils.shared import drive_auth, drive_pick
from xl_utils.shared.drive import DriveApiError, DriveClient, static_token


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--multiple",
        action="store_true",
        help="Permite escolher mais de um arquivo.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=drive_pick.PICK_TIMEOUT,
        help="Segundos de espera pelo seletor.",
    )
    return parser.parse_args()


def main() -> int:
    args = _arguments()
    try:
        client = drive_auth.load_client()
    except drive_auth.DriveError as error:
        print(f"ERRO: {error}")
        return 2

    try:
        picked = drive_pick.pick_files(
            client,
            multiple=args.multiple,
            timeout=args.timeout,
        )
    except drive_auth.DriveError as error:
        print(f"ERRO: {error}")
        return 1

    if picked.cancelled:
        print("Nenhum arquivo escolhido.")
        return 0

    api = DriveClient(static_token(picked.access_token))
    for file_id in picked.ids:
        try:
            metadata = api.metadata(file_id)
            data, name = api.payload(metadata)
        except DriveApiError as error:
            print(f"ERRO: {error}")
            return 1
        size = f"{len(data) / 1024:.1f} KB"
        print(f"OK: {name} ({metadata.mime_type}, {size})")

    print(f"Picker e Drive API funcionando: {len(picked.ids)} arquivo(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
