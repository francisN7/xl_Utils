"""Seleção pura de abas: mantém só o que o usuário marcou.

Entrada: mapa de abas e a coleção escolhida na UI.
Saída: novo mapa na ordem original.
Erros: ``ValueError`` para seleção vazia ou nome inexistente.
"""

from collections.abc import Collection, Mapping, Sequence
from pathlib import Path


def filter_sheets[Sheet](
    sheets: Mapping[str, Sheet],
    selected: Collection[str] | None = None,
) -> dict[str, Sheet]:
    """Mantém apenas as abas de ``selected``, preservando a ordem original.

    ``None`` significa "todas as abas". Seleção vazia ou nome inexistente
    levanta ``ValueError`` em vez de produzir um resultado vazio em silêncio.
    """
    if selected is None:
        return dict(sheets)

    chosen = set(selected)
    if not chosen:
        raise ValueError("Selecione ao menos uma aba para executar.")

    missing = [name for name in chosen if name not in sheets]
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"Aba(s) não encontrada(s): {names}.")

    return {name: frame for name, frame in sheets.items() if name in chosen}


def default_selection(
    sheets: Mapping[Path, Sequence[str]],
    *,
    all_sheets: bool = False,
) -> dict[Path, set[str]]:
    """Escolhe todas as abas de um arquivo e a primeira quando há vários.

    ``all_sheets=True`` marca todas as abas de todos os arquivos. As
    ferramentas em lote usam esse modo para que adicionar arquivo nunca esconda
    abas sem avisar; o merge mantém só a primeira de cada origem.
    """
    if all_sheets or len(sheets) <= 1:
        return {path: set(names) for path, names in sheets.items()}
    return {path: set(names[:1]) for path, names in sheets.items()}
