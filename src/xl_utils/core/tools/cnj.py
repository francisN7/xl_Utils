"""Extração pura de CNJ: encontra, padroniza e deduplica.

Entrada: mapa de abas ou um texto isolado.
Saída: lista ordenada de CNJs no formato pontuado ou a contagem de achados.
Erros: ``ValueError`` em ``normalize_cnj`` para valor inválido.
"""

import re
from collections.abc import Iterator, Mapping

import pandas as pd

# Separadores tolerados entre os blocos: espaço, quebra, ponto, barra e hífens.
_SEPARATOR = r"[\s./\-\u2010-\u2015\u2212]*"

# 20 dígitos: formato CNJ com separadores flexíveis ou sequência contínua. Os
# lookarounds impedem que um match comece ou termine dentro de um número maior
# (CPF, protocolo, etc.). O dígito verificador não é validado de propósito.
_CNJ_PATTERN = re.compile(
    rf"(?<![0-9])"
    rf"(?:[0-9]{{7}}{_SEPARATOR}[0-9]{{2}}{_SEPARATOR}[0-9]{{4}}"
    rf"{_SEPARATOR}[0-9]{_SEPARATOR}[0-9]{{2}}{_SEPARATOR}[0-9]{{4}}"
    rf"|[0-9]{{20}})"
    rf"(?![0-9])"
)

_INVISIBLE = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\u00ad\ufeff"))
_SPACES = str.maketrans({"\u00a0": " ", "\u2007": " ", "\u202f": " "})
_DASHES = str.maketrans(
    {
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2015": "-",
        "\u2212": "-",
    }
)


def _sanitize(text: str) -> str:
    """Remove invisíveis e uniformiza espaços e travessões só para a busca."""
    return text.translate(_INVISIBLE).translate(_SPACES).translate(_DASHES)


def extract_cnjs(text: str) -> list[str]:
    """Devolve cada valor com cara de CNJ em ``text``, na ordem de origem."""
    if not isinstance(text, str) or not text:
        return []
    clean = _sanitize(text)
    return [match.group(0) for match in _CNJ_PATTERN.finditer(clean)]


def normalize_cnj(value: str) -> str:
    """Converte um CNJ pontuado ou de 20 dígitos para o formato pontuado."""
    text = _sanitize(value).strip()
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


def summarize_cnjs(
    sheets: Mapping[str, pd.DataFrame],
) -> tuple[int, list[str]]:
    """Percorre as abas uma vez e devolve ``(achados, únicos ordenados)``.

    A UI precisa das duas informações no mesmo log; fazer uma passada só evita
    reler todas as células de planilhas grandes.
    """
    values = list(_iter_normalized(sheets))
    return len(values), sorted(set(values))


def collect_cnjs(sheets: Mapping[str, pd.DataFrame]) -> list[str]:
    """Normaliza todos os CNJs das abas e devolve uma lista única e ordenada."""
    return summarize_cnjs(sheets)[1]


def count_cnjs(sheets: Mapping[str, pd.DataFrame]) -> int:
    """Conta cada match, antes da deduplicação."""
    return summarize_cnjs(sheets)[0]


def _iter_normalized(sheets: Mapping[str, pd.DataFrame]) -> Iterator[str]:
    for frame in sheets.values():
        for row in frame.itertuples(index=False, name=None):
            for value in row:
                if not isinstance(value, str):
                    continue
                for match in extract_cnjs(value):
                    yield normalize_cnj(match)
