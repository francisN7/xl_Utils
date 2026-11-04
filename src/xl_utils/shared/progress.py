"""Progresso por arquivo durante a execução, sem conteúdo de célula."""

import contextlib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

ProgressKind = Literal["start", "file_started", "file_done", "finish"]

ProgressHandler = Callable[["ProgressEvent"], None]
ErrorHandler = Callable[[str], None]


@dataclass(frozen=True, slots=True)
class ProgressEvent:
    """Marco de uma execução: início, arquivo em andamento ou fim."""

    kind: ProgressKind
    total: int
    completed: int
    index: int = 0
    name: str = ""

    @property
    def text(self) -> str:
        """Devolve o texto exibido no painel, sem dados de célula."""
        if self.kind == "start":
            return f"Arquivo 0 de {self.total}"
        if self.kind == "file_started":
            return f"Arquivo {self.index} de {self.total}: {self.name}"
        if self.kind == "file_done":
            return f"Arquivo {self.completed} de {self.total} concluído(s)"
        return f"{self.completed} de {self.total} arquivo(s) concluído(s)"

    @property
    def value(self) -> float:
        """Devolve a fração concluída entre 0 e 1."""
        if self.total <= 0:
            return 0.0
        return min(max(self.completed / self.total, 0.0), 1.0)


class NullReporter:
    """Ignora os marcos de progresso (testes e execução síncrona)."""

    def start(self, total: int) -> None:
        """Marca o início de uma execução."""

    def file_started(self, name: str) -> None:
        """Marca o início do processamento de um arquivo."""

    def file_done(self, name: str = "") -> None:
        """Marca o fim do processamento de um arquivo."""

    def finish(self) -> None:
        """Marca o fim da execução."""


class ProgressReporter(NullReporter):
    """Converte os marcos em `ProgressEvent` e entrega ao callback."""

    def __init__(
        self,
        emit: ProgressHandler | None = None,
        *,
        on_error: ErrorHandler | None = None,
    ) -> None:
        self._emit = emit
        self._on_error = on_error
        self._total = 0
        self._completed = 0

    @property
    def total(self) -> int:
        """Devolve quantos arquivos foram declarados no início."""
        return self._total

    @property
    def completed(self) -> int:
        """Devolve quantos arquivos foram concluídos até agora."""
        return self._completed

    def start(self, total: int) -> None:
        """Reinicia a contagem para uma execução com `total` arquivos."""
        self._total = max(int(total), 0)
        self._completed = 0
        self._send("start")

    def file_started(self, name: str) -> None:
        """Emite o arquivo atual, contando a partir de um."""
        index = min(self._completed + 1, self._total)
        self._send("file_started", index=index, name=name)

    def file_done(self, name: str = "") -> None:
        """Acrescenta um arquivo concluído, sem passar do total."""
        if self._total:
            self._completed = min(self._completed + 1, self._total)
        self._send("file_done", name=name)

    def finish(self) -> None:
        """Emite o encerramento com a contagem real."""
        self._send("finish")

    def _send(
        self,
        kind: ProgressKind,
        *,
        index: int = 0,
        name: str = "",
    ) -> None:
        if self._emit is None:
            return
        event = ProgressEvent(
            kind=kind,
            total=self._total,
            completed=self._completed,
            index=index,
            name=name,
        )
        try:
            self._emit(event)
        except Exception as error:  # noqa: BLE001 - progresso nunca derruba a execução
            if self._on_error is not None:
                detail = f"Progresso indisponível: {type(error).__name__}: {error}"
                with contextlib.suppress(Exception):
                    self._on_error(detail)
