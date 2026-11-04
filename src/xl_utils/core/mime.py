"""Detect the real file format from its content, never from its name."""

from pathlib import Path

import puremagic

SUPPORTED_SUFFIXES = frozenset({".csv", ".htm", ".html", ".xls", ".xlsm", ".xlsx"})


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
    original = path.suffix.lower()
    detected = detect_suffix(path)
    if detected in SUPPORTED_SUFFIXES:
        return detected
    if original in SUPPORTED_SUFFIXES:
        return original
    return detected or original
