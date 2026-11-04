"""Pure CNJ extraction: find, standardize and deduplicate."""

import re
from collections.abc import Iterator, Mapping

import pandas as pd

# 20 consecutive digits or the punctuated CNJ format. Lookarounds stop a match
# from starting or ending inside a longer number.
_CNJ_PATTERN = re.compile(
    r"(?<![0-9])"
    r"(?:[0-9]{7}-[0-9]{2}\.[0-9]{4}\.[0-9]\.[0-9]{2}\.[0-9]{4}"
    r"|[0-9]{20})"
    r"(?![0-9])"
)


def extract_cnjs(text: str) -> list[str]:
    """Return every CNJ-like value found in ``text``, in source order."""
    if not isinstance(text, str) or not text:
        return []
    return [match.group(0) for match in _CNJ_PATTERN.finditer(text)]


def normalize_cnj(value: str) -> str:
    """Convert a punctuated or 20-digit CNJ to the punctuated format."""
    text = value.strip()
    if not _CNJ_PATTERN.fullmatch(text):
        raise ValueError(
            "CNJ inválido: esperado 20 dígitos ou o formato pontuado, "
            f"recebido {value!r}."
        )

    digits = re.sub(r"[^0-9]", "", text)
    return (
        f"{digits[:7]}-{digits[7:9]}.{digits[9:13]}."
        f"{digits[13]}.{digits[14:16]}.{digits[16:]}"
    )


def collect_cnjs(sheets: Mapping[str, pd.DataFrame]) -> list[str]:
    """Normalize every CNJ in all sheets and return a sorted unique list."""
    return sorted(set(_iter_normalized(sheets)))


def count_cnjs(sheets: Mapping[str, pd.DataFrame]) -> int:
    """Count every match, before deduplication."""
    return sum(1 for _ in _iter_normalized(sheets))


def _iter_normalized(sheets: Mapping[str, pd.DataFrame]) -> Iterator[str]:
    for frame in sheets.values():
        for row in frame.itertuples(index=False, name=None):
            for value in row:
                if not isinstance(value, str):
                    continue
                for match in extract_cnjs(value):
                    yield normalize_cnj(match)
