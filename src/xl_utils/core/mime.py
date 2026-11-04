"""Detect the real file format from its content, never from its name."""

from dataclasses import dataclass
from pathlib import Path

import puremagic

SUPPORTED_SUFFIXES = frozenset({".csv", ".htm", ".html", ".xls", ".xlsm", ".xlsx"})


@dataclass(frozen=True, slots=True)
class FormatCheck:
    """What the content says, what the name says and what will be read."""

    path: Path
    detected: str | None
    declared: str
    effective: str

    @property
    def identified(self) -> bool:
        """Return whether content or name points to a supported format."""
        return self.effective in SUPPORTED_SUFFIXES

    @property
    def diverges(self) -> bool:
        """Return whether the content points to another supported format."""
        return (
            self.identified
            and self.detected in SUPPORTED_SUFFIXES
            and self.detected != self.declared
        )

    @property
    def reason(self) -> str:
        """Describe the detected and declared suffixes for the UI."""
        detected = self.detected or "desconhecido"
        declared = self.declared or "sem extensão"
        return f"conteúdo: {detected} · nome: {declared}"

    @property
    def summary(self) -> str:
        """Describe the check for the log and the diagnostics."""
        detected = self.detected or "desconhecido"
        declared = self.declared or "sem extensão"
        if not self.identified:
            return f"não identificado (conteúdo {detected} · nome {declared})"
        return f"conteúdo {detected} · nome {declared} · leitura {self.effective}"


def detect_suffix(path: Path) -> str | None:
    """Return the extension detected from the file content.

    Returns ``None`` when the content cannot be identified.
    """
    try:
        suffix = puremagic.from_file(path)
    except puremagic.PureError, OSError:
        return None
    return suffix.lower() or None


def resolve_suffix(path: Path) -> str:
    """Pick the suffix used to read the file.

    Real content wins over the original name, but generic detections such as
    ``.txt`` fall back to the original suffix when it is a supported format.
    The file itself is never renamed.
    """
    return _pick_suffix(path.suffix.lower(), detect_suffix(path))


def check_format(path: Path) -> FormatCheck:
    """Summarize the detected, declared and effective suffixes of one file."""
    declared = path.suffix.lower()
    detected = detect_suffix(path)
    return FormatCheck(
        path=path,
        detected=detected,
        declared=declared,
        effective=_pick_suffix(declared, detected),
    )


def _pick_suffix(declared: str, detected: str | None) -> str:
    if detected in SUPPORTED_SUFFIXES:
        return detected
    if declared in SUPPORTED_SUFFIXES:
        return declared
    return detected or declared
