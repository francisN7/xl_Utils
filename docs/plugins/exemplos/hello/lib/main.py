"""Exemplo mínimo: uma linha de resumo por aba escolhida."""

import pandas as pd

from xl_utils.shared.plugins.api import PluginRequest, PluginResult


def run(request: PluginRequest) -> PluginResult:
    """Conta as linhas de cada aba marcada e devolve a tabela."""
    pairs = [(path, name) for path, names in request.sheets.items() for name in names]
    request.progress.start(len(pairs))
    rows: list[dict[str, object]] = []
    for path, name in pairs:
        if request.cancel.cancelled:
            break
        request.progress.file_started(f"{path.name} · {name}")
        frame = pd.read_excel(path, sheet_name=name, engine="openpyxl")
        rows.append({"arquivo": path.name, "aba": name, "linhas": len(frame)})
        request.log.info(f"{path.name} · {name}: {len(frame)} linha(s)")
        request.progress.file_done(f"{path.name} · {name}")
    request.progress.finish()
    if not rows:
        return PluginResult(message="Nenhuma aba selecionada.")
    return PluginResult(
        frames={"resumo": pd.DataFrame(rows)},
        message=f"{len(rows)} aba(s) lida(s)",
    )
