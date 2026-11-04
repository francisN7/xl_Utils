"""Log estruturado de execução e diagnóstico copiável."""

import platform
import traceback as traceback_lib
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Literal

from xl_utils.core.mime import FormatCheck

LogLevel = Literal["info", "success", "warning", "error"]

_LABELS: dict[LogLevel, str] = {
    "info": "INFO",
    "success": "OK",
    "warning": "AVISO",
    "error": "ERRO",
}

_MAX_TRACEBACK = 4000


@dataclass(frozen=True, slots=True)
class LogEvent:
    """Um passo da execução, com o seu nível."""

    level: LogLevel
    text: str

    def to_line(self) -> str:
        """Devolve o evento como uma linha exibível."""
        if not self.text:
            return ""
        return f"[{_LABELS[self.level]}] {self.text}"


class RunLog:
    """Eventos ordenados produzidos durante a execução de uma ferramenta."""

    def __init__(self, events: Iterable[LogEvent] = ()) -> None:
        self._events: list[LogEvent] = list(events)

    @property
    def events(self) -> tuple[LogEvent, ...]:
        """Devolve os eventos registrados, preservando a ordem."""
        return tuple(self._events)

    def add(self, level: LogLevel, text: str) -> RunLog:
        """Acrescenta um evento e devolve o log para encadeamento."""
        self._events.append(LogEvent(level, text))
        return self

    def info(self, text: str) -> RunLog:
        """Registra um passo normal."""
        return self.add("info", text)

    def success(self, text: str) -> RunLog:
        """Registra um passo concluído."""
        return self.add("success", text)

    def warning(self, text: str) -> RunLog:
        """Registra algo que o usuário deve notar."""
        return self.add("warning", text)

    def error(self, text: str) -> RunLog:
        """Registra uma falha."""
        return self.add("error", text)

    def extend(self, events: RunLog | Iterable[str]) -> RunLog:
        """Acrescenta outro log, ou linhas simples tratadas como eventos info."""
        if isinstance(events, RunLog):
            self._events.extend(events.events)
        else:
            self._events.extend(LogEvent("info", str(line)) for line in events)
        return self

    def to_text(self) -> str:
        """Devolve uma linha por evento."""
        return "\n".join(self)

    def __iter__(self) -> Iterator[str]:
        """Percorre as linhas formatadas, mantendo o log compatível com lista."""
        return (event.to_line() for event in self._events)

    def __len__(self) -> int:
        return len(self._events)

    def __bool__(self) -> bool:
        return bool(self._events)


def app_versions() -> dict[str, str]:
    """Devolve as versões exibidas no diagnóstico."""
    return {
        "App": _package_version("xl-utils"),
        "Python": platform.python_version(),
        "pandas": _package_version("pandas"),
        "Flet": _package_version("flet"),
    }


def build_diagnostics(
    *,
    tool: str = "",
    files: Sequence[Path] = (),
    sheets: Mapping[Path, Sequence[str]] | None = None,
    formats: Mapping[Path, FormatCheck] | None = None,
    options: Mapping[str, object] | None = None,
    message: str = "",
    error: BaseException | None = None,
    traceback_text: str | None = None,
    versions: Mapping[str, str] | None = None,
) -> str:
    """Monta o texto copiável do diagnóstico de uma execução.

    Inclui versões, arquivos (caminho, formato e abas escolhidas), opções,
    resultado, erro e traceback truncado. Não inclui conteúdo de célula: as
    abas entram só pelo nome, e as colunas, por nome de arquivo, aba e coluna.
    """
    lines = ["Diagnóstico — xl_utils"]

    if tool:
        lines.append(f"Ferramenta: {tool}")

    lines += ["", "Versões:"]
    lines.extend(
        f"  {name}: {value}" for name, value in (versions or app_versions()).items()
    )

    if files:
        lines += ["", "Arquivos:"]
        for path in files:
            lines.append(f"  {path}")
            check = (formats or {}).get(path)
            if check is not None:
                lines.append(f"    Formato: {check.summary}")
                if check.diverges:
                    lines.append("    Divergência: conteúdo difere da extensão")
            selected = (sheets or {}).get(path)
            if selected:
                names = ", ".join(sorted(str(name) for name in selected))
                lines.append(f"    Abas: {names}")

    usable_options = {
        name: value for name, value in (options or {}).items() if _has_value(value)
    }
    if usable_options:
        lines += ["", "Opções:"]
        lines.extend(
            f"  {name}: {_format_value(value)}"
            for name, value in usable_options.items()
        )

    if message:
        lines += ["", f"Resultado: {message}"]

    if error is not None:
        lines += [
            "",
            "Erro:",
            f"  Tipo: {type(error).__name__}",
            f"  Mensagem: {error}",
        ]
        cause = error.__cause__ or error.__context__
        if cause is not None:
            lines.append(f"  Causa: {type(cause).__name__}: {cause}")

        trace = traceback_text
        if trace is None:
            trace = "".join(
                traceback_lib.format_exception(type(error), error, error.__traceback__)
            )
        trace = trace.strip()
        if trace:
            if len(trace) > _MAX_TRACEBACK:
                trace = f"{trace[:_MAX_TRACEBACK]}\n[... truncado]"
            lines += ["", "Traceback:", trace]

    return "\n".join(lines)


def _package_version(distribution: str) -> str:
    try:
        return metadata.version(distribution)
    except metadata.PackageNotFoundError:
        return "desconhecida"


def _has_value(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, frozenset, dict)):
        return bool(value)
    return True


def _format_value(value: object) -> str:
    if (
        hasattr(value, "source")
        and hasattr(value, "sheet")
        and hasattr(value, "column")
    ):
        source = Path(str(value.source)).name
        return f"{source} · {value.sheet} · {value.column}"
    if isinstance(value, Mapping):
        items = ", ".join(f"{key}={_format_value(item)}" for key, item in value.items())
        return "{" + items + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_format_value(item) for item in value) + "]"
    if isinstance(value, (set, frozenset)):
        ordered = sorted(value, key=str)
        return "[" + ", ".join(_format_value(item) for item in ordered) + "]"
    return str(value)
