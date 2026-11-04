"""Pure sheet selection: keep only the sheets the user marked."""

from collections.abc import Collection, Mapping, Sequence
from pathlib import Path


def filter_sheets[Sheet](
    sheets: Mapping[str, Sheet],
    selected: Collection[str] | None = None,
) -> dict[str, Sheet]:
    """Keep only ``selected`` sheets, preserving the original order.

    ``None`` means "all sheets". An empty selection or a name that does not
    exist raises ``ValueError`` instead of silently producing nothing.
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
    """Pick every sheet for one file and the first sheet for several files.

    ``all_sheets=True`` marks every sheet of every file instead; the batch
    tools use it so adding files never hides sheets without telling the user.
    """
    if all_sheets or len(sheets) <= 1:
        return {path: set(names) for path, names in sheets.items()}
    return {path: set(names[:1]) for path, names in sheets.items()}
