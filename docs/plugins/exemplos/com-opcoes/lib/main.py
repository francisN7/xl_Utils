"""Exemplo com opções tipadas, slots nomeados, log e progresso."""

import pandas as pd

from xl_utils.shared.plugins.api import PluginRequest, PluginResult

COLUMN_LIMIT = 6


def run(request: PluginRequest) -> PluginResult:
    """Resume as abas da origem e, se marcado, da planilha de apoio."""
    sources = _sources(request)
    if not sources:
        return PluginResult(message="Escolha a planilha de origem.")

    titulo = str(request.options["titulo"])
    limite = int(request.options["limite"])
    modo = str(request.options["modo"])
    rows: list[dict[str, object]] = []
    request.progress.start(len(sources))
    for path in sources:
        if request.cancel.cancelled:
            break
        request.progress.file_started(path.name)
        for name in request.sheets.get(path, ()):
            if request.cancel.cancelled:
                break
            frame = pd.read_excel(
                path,
                sheet_name=name,
                nrows=limite,
                engine="openpyxl",
            )
            rows.append(
                {
                    "titulo": titulo,
                    "arquivo": path.name,
                    "aba": name,
                    "modo": modo,
                    "resultado": _value(frame, modo),
                }
            )
            request.log.info(f"{path.name} · {name}: {len(frame)} linha(s)")
        request.progress.file_done(path.name)
    request.progress.finish()
    if not rows:
        return PluginResult(message="Nenhuma aba selecionada.")
    return PluginResult(
        frames={"resumo": pd.DataFrame(rows)},
        message=f"{titulo}: {len(rows)} aba(s)",
    )


def _sources(request: PluginRequest) -> list:
    """Monta a lista de planilhas na ordem em que aparecem na tela."""
    sources = []
    origem = request.inputs.get("origem")
    if origem is not None:
        sources.append(origem)
    apoio = request.inputs.get("apoio")
    if apoio is not None and bool(request.options["incluir_apoio"]):
        sources.append(apoio)
    return sources


def _value(frame: pd.DataFrame, modo: str) -> str | int:
    if modo == "colunas":
        columns = [str(column) for column in frame.columns[:COLUMN_LIMIT]]
        restante = len(frame.columns) - len(columns)
        return ", ".join(columns) + (f" (+{restante})" if restante else "")
    return len(frame)
