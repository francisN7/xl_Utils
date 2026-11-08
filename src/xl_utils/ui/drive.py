"""Estado do Drive compartilhado pelo menu do topo e pela tela inicial."""

from __future__ import annotations

import asyncio
import shutil
from collections.abc import Callable
from pathlib import Path

from xl_utils.shared import accounts, drive_auth, drive_cache, drive_pick
from xl_utils.shared.accounts import Account, AccountStore
from xl_utils.shared.drive import DriveClient, static_token, token_provider


class DriveSession:
    """Contas, conta ativa e o login em andamento.

    O login roda fora da thread da UI; quem escuta recebe um aviso quando o
    estado muda e só então redesenha os controles.
    """

    def __init__(
        self,
        store: AccountStore | None = None,
        authorize: Callable[[], Account] | None = None,
        *,
        configured: bool | None = None,
        picker: Callable[..., drive_pick.PickedFiles] | None = None,
        client_factory: Callable[[Account], DriveClient] | None = None,
        cache_root: Path | None = None,
    ) -> None:
        self._store = store or AccountStore()
        self._authorize = authorize or drive_auth.authorize
        self._picker = picker or drive_pick.pick_files
        self._client_factory = client_factory or _client_for
        self._cache_root = cache_root
        self._listeners: list[Callable[[], None]] = []
        self.accounts: list[Account] = []
        self.active: str | None = None
        self.busy = False
        self.error: str | None = None
        self.configured = (
            drive_auth.is_configured() if configured is None else configured
        )
        self.reload()

    @property
    def active_account(self) -> Account | None:
        """Devolve o registro da conta ativa, se houver."""
        for account in self.accounts:
            if account.email == self.active:
                return account
        return None

    def subscribe(self, listener: Callable[[], None]) -> None:
        """Registra um redesenho para quando o estado mudar."""
        self._listeners.append(listener)

    def reload(self) -> None:
        """Relê as contas e a conta ativa do disco."""
        self.accounts = self._store.list()
        self.active = self._store.active()

    def notify(self) -> None:
        """Avisa todos os controles inscritos."""
        for listener in self._listeners:
            listener()

    async def connect(self) -> None:
        """Abre o navegador e guarda a conta autorizada, fora da UI thread."""
        if self.busy:
            return
        if not self.configured:
            self.error = "Configure o cliente OAuth do Drive antes de entrar."
            self.notify()
            return
        self.busy = True
        self.error = None
        self.notify()
        try:
            account = await asyncio.to_thread(self._authorize)
            self._store.save(account)
            self._store.set_active(account.email)
        except (drive_auth.DriveError, accounts.AccountsError) as error:
            self.error = str(error)
        except Exception:  # noqa: BLE001 - nunca vazar token ou traceback
            self.error = "Falha inesperada ao entrar no Google Drive."
        finally:
            self.busy = False
            self.reload()
            self.notify()

    async def open_from_drive(
        self,
        account: Account | None = None,
        *,
        multiple: bool = False,
    ) -> list[Path]:
        """Escolhe planilhas no Drive e devolve cópias locais temporárias.

        O Picker, o download e a gravação no cache rodam fora da UI thread. Um
        cancelamento não é erro: devolve lista vazia e nenhuma mensagem.
        """
        if self.busy:
            return []
        target = account or self.active_account
        if target is None:
            self.error = "Entre no Google Drive para abrir uma planilha de lá."
            self.notify()
            return []
        self.busy = True
        self.error = None
        self.notify()
        try:
            paths = await asyncio.to_thread(self._open_sync, target, multiple)
        except (drive_auth.DriveError, accounts.AccountsError) as error:
            self.error = str(error)
            paths = []
        except Exception:  # noqa: BLE001 - nunca vazar token ou traceback
            self.error = "Falha inesperada ao abrir do Google Drive."
            paths = []
        finally:
            self.busy = False
            self.notify()
        return paths

    def _open_sync(self, account: Account, multiple: bool) -> list[Path]:
        """Parte bloqueante de :meth:`open_from_drive`."""
        selection = self._picker(multiple=multiple, login_hint=account.email)
        if selection.cancelled:
            return []
        client = (
            self._client_for_pick(selection.access_token)
            if selection.access_token
            else self._client_factory(account)
        )
        directory = drive_cache.new_session(self._cache_root)
        try:
            paths: list[Path] = []
            for file_id in selection.ids:
                metadata = client.metadata(file_id)
                data, name = client.payload(metadata)
                paths.append(drive_cache.store(directory, name, data))
        except Exception:
            shutil.rmtree(directory, ignore_errors=True)
            raise
        return paths

    def _client_for_pick(self, token: str) -> DriveClient:
        """Cliente que usa o token curto devolvido pelo próprio Picker."""
        return DriveClient(static_token(token))

    def import_client(self, path: Path) -> None:
        """Importa o JSON do cliente OAuth escolhido pelo usuário."""
        try:
            drive_auth.import_client(path)
        except (drive_auth.DriveError, OSError) as error:
            self.error = str(error)
        else:
            self.configured = True
            self.error = None
        self.notify()

    def switch(self, email: str) -> None:
        """Troca a conta ativa sem apagar nenhuma outra."""
        try:
            self._store.set_active(email)
            self.error = None
        except accounts.AccountsError as error:
            self.error = str(error)
        self.reload()
        self.notify()

    def next_account(self) -> str | None:
        """Devolve o próximo e-mail da lista, para o botão “Trocar”."""
        if len(self.accounts) < 2:
            return None
        emails = [account.email for account in self.accounts]
        if self.active not in emails:
            return emails[0]
        return emails[(emails.index(self.active) + 1) % len(emails)]

    def logout(self) -> None:
        """Remove só a conta ativa; as demais continuam guardadas."""
        if self.active is None:
            return
        self._store.remove(self.active)
        self._store.clear_active()
        self.error = None
        self.reload()
        self.notify()


def _client_for(account: Account) -> DriveClient:
    """Monta o cliente da Drive API com o refresh token da conta."""
    return DriveClient(token_provider(account, drive_auth.load_client()))
