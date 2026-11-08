#!/usr/bin/env python
"""Teste semi-automático do Picker do Drive com a conta real.

Abre o navegador, espera a escolha e imprime só o necessário: nome, tipo e
tamanho do arquivo baixado. Nunca imprime token, código ou segredo, e não grava
conta nenhuma.

Com ``--folder --write``, escolhe uma pasta e testa a gravação de um arquivo
pequeno com o token curto do Picker e com o token persistido da conta. É o teste
que decide se a S9c pode gravar ao lado da planilha de origem. Os arquivos de
teste são apagados no fim.

Uso:
    uv run python scripts/check-drive-picker.py
    uv run python scripts/check-drive-picker.py --multiple
    uv run python scripts/check-drive-picker.py --folder --write
    uv run python scripts/check-drive-picker.py --timeout 300
"""

from __future__ import annotations

import argparse
import sys
import uuid

from xl_utils.shared import accounts, drive_auth, drive_pick
from xl_utils.shared.drive import (
    DriveApiError,
    DriveClient,
    DriveFile,
    static_token,
    token_provider,
)


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--multiple",
        action="store_true",
        help="Permite escolher mais de um arquivo.",
    )
    parser.add_argument(
        "--folder",
        action="store_true",
        help="Permite escolher uma pasta em vez de um arquivo.",
    )
    parser.add_argument(
        "--parent-write",
        action="store_true",
        help="Testa gravar na pasta do arquivo escolhido, sem escolher a pasta.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Testa gravar e apagar um arquivo na pasta escolhida.",
    )
    parser.add_argument(
        "--account",
        default="",
        help="E-mail da conta salva a usar no seletor e na gravação.",
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
    folders = args.folder or args.write
    try:
        client = drive_auth.load_client()
    except drive_auth.DriveError as error:
        print(f"ERRO: {error}")
        return 2

    account = _pick_account(args.account)
    if account is not None:
        print(f"Conta salva usada no login_hint: {account.email}")
    try:
        if folders:
            print("No seletor, escolha uma PASTA (ícone de pasta), nao um arquivo.")
            if account is not None:
                print(f"Use a MESMA conta do app: {account.email}")
        picked = drive_pick.pick_files(
            client,
            multiple=args.multiple and not folders,
            folders=folders,
            login_hint=account.email if account else "",
            timeout=args.timeout,
        )
    except drive_auth.DriveError as error:
        print(f"ERRO: {error}")
        return 1

    if picked.cancelled:
        print("Nenhum item escolhido.")
        return 0

    api = DriveClient(static_token(picked.access_token))
    items: list[DriveFile] = []
    for item_id in picked.ids:
        try:
            items.append(api.metadata(item_id))
        except DriveApiError as error:
            print(f"ERRO: {error}")
            return 1

    if args.parent_write:
        return _parent_write(items, api, account)

    if not args.write:
        for metadata in items:
            if metadata.is_folder:
                print(f"OK: pasta {metadata.name} ({metadata.id})")
                continue
            try:
                data, name = api.payload(metadata)
            except DriveApiError as error:
                print(f"ERRO: {error}")
                return 1
            size = f"{len(data) / 1024:.1f} KB"
            print(f"OK: {name} ({metadata.mime_type}, {size})")
        print(f"Picker e Drive API funcionando: {len(picked.ids)} item(ns).")
        return 0

    folder = next((item for item in items if item.is_folder), None)
    if folder is None:
        for metadata in items:
            print(f"Escolhido: {metadata.name} ({metadata.mime_type})")
        print("ERRO: escolha uma pasta para testar a gravação.")
        return 1
    print(f"Pasta: {folder.name} ({folder.id})")
    try:
        print(f"Filhos visíveis antes: {len(api.children(folder.id, limit=100))}")
    except DriveApiError as error:
        print(f"AVISO: não foi possível listar os filhos: {error}")
    try:
        print(f"Raiz do Picker: {api.root_id()}")
    except DriveApiError as error:
        print(f"AVISO: raiz do Picker indisponível: {error}")
    try:
        print(f"Conta do Picker: {api.user_email()}")
    except DriveApiError as error:
        print(f"AVISO: e-mail do Picker indisponível: {error}")

    if account is None:
        print("ERRO: nenhuma conta persistida; entre no Drive pelo app primeiro.")
        return 1
    print(f"Conta da gravação: {account.email}")

    try:
        short_name, short_file = _probe(api, folder.id, "picker")
        print(f"Escrita com token do Picker: OK ({short_name})")
        api.delete(short_file.id)
        print("Limpeza do token do Picker: OK")
    except DriveApiError as error:
        print(f"ERRO na escrita com token do Picker: {error}")
        return 1

    try:
        account_api = DriveClient(token_provider(account, client))
        print(f"Escopos da conta: {' '.join(account.scopes) or '(vazio)'}")
        try:
            print(f"Raiz da conta: {account_api.root_id()}")
        except DriveApiError as error:
            print(f"AVISO: raiz da conta indisponível: {error}")
        try:
            print(f"E-mail da conta pelo Drive: {account_api.user_email()}")
        except DriveApiError as error:
            print(f"AVISO: e-mail da conta indisponível: {error}")
        try:
            visible = account_api.metadata(folder.id)
            print(f"Pasta vista pela conta: {visible.name}")
        except DriveApiError as error:
            print(f"AVISO: a conta não vê a pasta: {error}")
        account_name, account_file = _probe(account_api, folder.id, "conta")
        print(f"Escrita com token da conta: OK ({account_name})")
        account_api.delete(account_file.id)
        print("Limpeza do token da conta: OK")
    except DriveApiError as error:
        print(f"ERRO na escrita com token da conta: {error}")
        print("A concessão de pasta não sobreviveu à conta persistida.")
        return 1

    print("Concessão de pasta funcionando para as duas autorizações.")
    return 0


def _parent_write(
    items: list[DriveFile],
    api: DriveClient,
    account: accounts.Account | None,
) -> int:
    """Tenta gravar na pasta do arquivo escolhido, sem escolher a pasta."""
    file = next((item for item in items if not item.is_folder), None)
    if file is None:
        print("ERRO: escolha um arquivo (não uma pasta) para este teste.")
        return 1
    print(f"Arquivo: {file.name}")
    if not file.parents:
        print("ERRO: o Google não devolveu a pasta do arquivo.")
        return 1
    parent = file.parents[0]
    print(f"Pasta do arquivo: {parent}")
    if account is None:
        print("ERRO: nenhuma conta persistida; entre no Drive pelo app primeiro.")
        return 1
    print(f"Conta da gravação: {account.email}")
    client = drive_auth.load_client()

    try:
        name, uploaded = _probe(api, parent, "picker-pai")
        print(f"Escrita na pasta com token do Picker: OK ({name})")
        api.delete(uploaded.id)
        print("Limpeza: OK")
    except DriveApiError as error:
        print(f"ERRO na escrita com token do Picker: {error}")
        return 1

    try:
        account_api = DriveClient(token_provider(account, client))
        name, uploaded = _probe(account_api, parent, "conta-pai")
        print(f"Escrita na pasta com token da conta: OK ({name})")
        account_api.delete(uploaded.id)
        print("Limpeza da conta: OK")
    except DriveApiError as error:
        print(f"ERRO na escrita com token da conta: {error}")
        print("A pasta do arquivo escolhido não recebe gravação direta.")
        return 1

    print(
        "A pasta do arquivo escolhido aceita gravação: não precisa de Picker de pasta."
    )
    return 0


def _pick_account(email: str = "") -> accounts.Account | None:
    store = accounts.AccountStore()
    if email:
        found = store.get(email)
        if found is not None:
            return found
    active = store.active()
    if active:
        found = store.get(active)
        if found is not None:
            return found
    saved = store.list()
    return saved[0] if saved else None


def _probe(
    api: DriveClient,
    parent: str,
    label: str,
) -> tuple[str, DriveFile]:
    name = f"xl_utils-teste-{label}-{uuid.uuid4().hex[:8]}.txt"
    if api.exists(parent, name):
        raise DriveApiError("O nome de teste já existia na pasta.")
    uploaded = api.upload(
        name,
        b"xl_utils: teste de gravacao",
        parent=parent,
        mime_type="text/plain",
    )
    if not api.exists(parent, name):
        raise DriveApiError("O arquivo gravado não apareceu na listagem da pasta.")
    return name, uploaded


if __name__ == "__main__":
    sys.exit(main())
