"""Exemplo mínimo: uma linha de resumo por aba escolhida."""

import pandas as pd

from xl_utils.shared.plugins.api import PluginRequest, PluginResult


def run(request: PluginRequest) -> PluginResult:
    """Conta as linhas de cada aba marcada e devolve a tabela."""
    request.progress.start(len(request.files))
    rows: list[dict[str, object]] = []
    for path in request.files:
        if request.cancel.cancelled:
            break
        request.progress.file_started(path.name)
        # O reader devolve só as abas marcadas, já como texto e sem emojis.
        for name, frame in request.reader.read(path).items():
            rows.append({"arquivo": path.name, "aba": name, "linhas": len(frame)})
            request.log.info(f"{path.name} · {name}: {len(frame)} linha(s)")
        request.progress.file_done(path.name)
    request.progress.finish()
    if not rows:
        return PluginResult(message="Nenhuma aba selecionada.")
    return PluginResult(
        frames={"resumo": pd.DataFrame(rows)},
        message=f"{len(rows)} aba(s) lida(s)",
    )
