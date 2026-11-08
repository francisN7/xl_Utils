#!/usr/bin/env python
"""Teste semi-automático do login real no Google Drive.

Abre o navegador, espera o retorno e imprime só o necessário: e-mail, nome,
escopos e a presença do refresh token. Nunca imprime token, código ou segredo,
e não grava conta nenhuma — quem grava é o aplicativo.

Uso:
    uv run python scripts/check-drive-login.py
    uv run python scripts/check-drive-login.py --import-file client_secret_....json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from xl_utils.shared import drive_auth


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--import-file",
        type=Path,
        help="JSON do cliente OAuth baixado do Google Cloud Console.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=drive_auth.LOGIN_TIMEOUT,
        help="Segundos de espera pelo navegador.",
    )
    return parser.parse_args()


def main() -> int:
    args = _arguments()
    try:
        if args.import_file is not None:
            drive_auth.import_client(args.import_file)
            print(f"Cliente importado para {drive_auth.client_path()}.")
        client = drive_auth.load_client()
    except drive_auth.DriveError as error:
        print(f"ERRO: {error}")
        return 2

    try:
        account = drive_auth.authorize(client, timeout=args.timeout)
    except drive_auth.DriveError as error:
        print(f"ERRO: {error}")
        return 1

    print(f"OK: {account.email}")
    if account.name:
        print(f"Nome: {account.name}")
    print(f"Escopos: {', '.join(account.scopes)}")
    print("Refresh token: presente")
    return 0


if __name__ == "__main__":
    sys.exit(main())
