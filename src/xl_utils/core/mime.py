"""Detecta o formato real pelo conteúdo do arquivo, nunca pelo nome.

Entrada: caminho de um arquivo qualquer.
Saída: sufixo detectado/efetivo ou um ``FormatCheck`` imutável.
Erros: nenhum; conteúdo ilegível vira ``None`` e a extensão decide.
"""

from dataclasses import dataclass
from pathlib import Path

import puremagic

SUPPORTED_SUFFIXES = frozenset({".csv", ".htm", ".html", ".xls", ".xlsm", ".xlsx"})

# Formatos que o leitor trata igual. Sem isso, um ``.xlsm`` detectado como
# ``.xlsx`` (mesmo container zip) apareceria como divergência em toda macro.
_EQUIVALENT_SUFFIXES = (
    frozenset({".xlsx", ".xlsm"}),
    frozenset({".htm", ".html"}),
)


@dataclass(frozen=True, slots=True)
class FormatCheck:
    """O que o conteúdo diz, o que o nome diz e o que será lido."""

    path: Path
    detected: str | None
    declared: str
    effective: str

    @property
    def identified(self) -> bool:
        """Indica se conteúdo ou nome aponta para um formato suportado."""
        return self.effective in SUPPORTED_SUFFIXES

    @property
    def diverges(self) -> bool:
        """Indica se o conteúdo aponta para outro formato suportado.

        Formatos equivalentes (``.xlsx``/``.xlsm`` e ``.htm``/``.html``) não
        contam como divergência: a leitura é a mesma.
        """
        return (
            self.identified
            and self.detected in SUPPORTED_SUFFIXES
            and self.detected != self.declared
            and not _same_family(self.detected or "", self.declared)
        )

    @property
    def reason(self) -> str:
        """Descreve os sufixos detectado e declarado para a UI."""
        detected = self.detected or "desconhecido"
        declared = self.declared or "sem extensão"
        return f"conteúdo: {detected} · nome: {declared}"

    @property
    def summary(self) -> str:
        """Descreve a checagem para o log e o diagnóstico."""
        detected = self.detected or "desconhecido"
        declared = self.declared or "sem extensão"
        if not self.identified:
            return f"não identificado (conteúdo {detected} · nome {declared})"
        return f"conteúdo {detected} · nome {declared} · leitura {self.effective}"


def detect_suffix(path: Path) -> str | None:
    """Devolve a extensão detectada pelo conteúdo.

    Retorna ``None`` quando o conteúdo não pode ser identificado.
    """
    try:
        suffix = puremagic.from_file(path)
    except puremagic.PureError, OSError:
        return None
    return suffix.lower() or None


def resolve_suffix(path: Path) -> str:
    """Escolhe o sufixo usado para ler o arquivo.

    O conteúdo real vence o nome original, mas detecções genéricas como ``.txt``
    caem para a extensão original quando ela é suportada. O arquivo nunca é
    renomeado.
    """
    return _pick_suffix(path.suffix.lower(), detect_suffix(path))


def check_format(path: Path) -> FormatCheck:
    """Resume os sufixos detectado, declarado e efetivo de um arquivo."""
    declared = path.suffix.lower()
    detected = detect_suffix(path)
    return FormatCheck(
        path=path,
        detected=detected,
        declared=declared,
        effective=_pick_suffix(declared, detected),
    )


def _pick_suffix(declared: str, detected: str | None) -> str:
    """Aplica a precedência: conteúdo suportado > extensão suportada > resto."""
    if detected in SUPPORTED_SUFFIXES:
        return detected
    if declared in SUPPORTED_SUFFIXES:
        return declared
    return detected or declared


def _same_family(left: str, right: str) -> bool:
    """Indica se dois sufixos usam o mesmo leitor."""
    return any({left, right} <= group for group in _EQUIVALENT_SUFFIXES)
