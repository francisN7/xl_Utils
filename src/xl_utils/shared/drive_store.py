"""Pastas do Drive que o usuário autorizou a receber gravações.

O escopo ``drive.file`` concede acesso arquivo por arquivo. Para gravar numa
pasta, o usuário precisa escolhê-la uma vez no Picker; o Google passa a ligar
essa concessão ao app. Este módulo guarda, por conta, quais pastas já foram
escolhidas para não pedir de novo.

Entrada: e-mail da conta e ID da pasta.
Saída: :class:`FolderGrant` ou ``None``.
Erros: :class:`DriveStoreError` ao gravar; leitura corrompida é ignorada.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from xl_utils.shared.accounts import default_root
from xl_utils.shared.drive_auth import DriveError

FOLDER_FILE = "folders.json"


class DriveStoreError(DriveError):
    """Não foi possível ler ou gravar a lista de pastas autorizadas."""


@dataclass(frozen=True, slots=True)
class FolderGrant:
    """Uma pasta que o app pode usar como destino de gravação."""

    folder_id: str
    name: str = ""


class FolderStore:
    """Lista de pastas concedidas, uma entrada por conta."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or default_root()

    @property
    def path(self) -> Path:
        """Arquivo com as concessões, no mesmo diretório das contas."""
        return self.root / FOLDER_FILE

    def grants(self, email: str) -> dict[str, FolderGrant]:
        """Devolve as pastas concedidas à conta, por ID."""
        raw = self._read().get(_email(email))
        if not isinstance(raw, dict):
            return {}
        grants: dict[str, FolderGrant] = {}
        for folder_id, value in raw.items():
            if not isinstance(folder_id, str) or not folder_id:
                continue
            name = value.get("name") if isinstance(value, dict) else ""
            grants[folder_id] = FolderGrant(
                folder_id=folder_id,
                name=name if isinstance(name, str) else "",
            )
        return grants

    def get(self, email: str, folder_id: str) -> FolderGrant | None:
        """Devolve a concessão da pasta, se ela já foi escolhida."""
        if not folder_id:
            return None
        return self.grants(email).get(folder_id)

    def save(self, email: str, folder_id: str, name: str = "") -> FolderGrant:
        """Guarda (ou renova) a concessão de uma pasta."""
        if not folder_id.strip():
            raise DriveStoreError("A pasta escolhida não tem identificador.")
        data = self._read()
        key = _email(email)
        account = data.get(key)
        if not isinstance(account, dict):
            account = {}
            data[key] = account
        account[folder_id] = {"name": name.strip()}
        self._write(data)
        return FolderGrant(folder_id=folder_id, name=name.strip())

    def forget(self, email: str, folder_id: str) -> None:
        """Remove a concessão; a próxima gravação pergunta de novo."""
        data = self._read()
        key = _email(email)
        account = data.get(key)
        if not isinstance(account, dict) or folder_id not in account:
            return
        del account[folder_id]
        if account:
            data[key] = account
        else:
            data.pop(key, None)
        self._write(data)

    def clear(self, email: str) -> None:
        """Esquece todas as pastas da conta, por exemplo ao sair."""
        data = self._read()
        if data.pop(_email(email), None) is not None:
            self._write(data)

    def _read(self) -> dict[str, Any]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except OSError, ValueError:
            return {}
        return data if isinstance(data, dict) else {}

    def _write(self, data: dict[str, Any]) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_name(f"{self.path.name}.tmp")
            temporary.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(temporary, self.path)
        except OSError as error:
            raise DriveStoreError(
                "Não foi possível guardar a pasta autorizada do Google Drive."
            ) from error


def _email(value: str) -> str:
    return value.strip().lower()


__all__ = ["DriveStoreError", "FolderGrant", "FolderStore"]
