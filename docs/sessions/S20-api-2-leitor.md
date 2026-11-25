# S20 — Leitura de planilhas pelo host e API 2 dos plugins

## Objetivo

Plugin com `api_version = 2` lê planilhas por `request.reader`, com o mesmo
pipeline das ferramentas nativas (`all_str`: texto, emojis, reparo, CSV/HTML),
inclusive arquivos do cache do Drive; a API 1 deixa de ser aceita.

## Fora de escopo

- Reescrever a vinculação como plugin (S02 do `xl_U-Plugins`).
- Sandbox, download ou atualização automática, UI própria de plugin.
- Menu de perfis do Drive (S21).

## Tarefas

1. Decidir a forma do `reader` (métodos, retorno, erros, cancelamento) por
   questionário e registrar em ADR novo ou adendo do 0023.
2. `shared/plugins/api.py`: `PluginRequest.reader`, apoiado em
   `core/tools/all_str.prepare_workbook`, sem o plugin importar `core/`.
3. `core/plugins/manifest.py`: `API_VERSION = 2`,
   `SUPPORTED_API_VERSIONS = {2}`; manifesto com `1` é recusado com motivo.
4. `controllers/plugins.py`: montar o `reader`; arquivo do cache do Drive
   chega como `Path` local, igual ao do computador.
5. Docs `docs/plugins/` (`api.md`, `manifesto.md`, `versionamento.md`,
   `primeiro-plugin.md`) e os dois exemplos em `exemplos/` para a API 2.
6. Testes: `reader` nos quatro formatos, arquivo do cache do Drive, recusa da
   API 1, exemplos rodando.
7. No `xl_U-Plugins`: `_molde/` na API 2 e `check` verde (commit local lá).

## Aceite

- [ ] Exemplo com API 2 lê `.xlsx`, `.xls`, `.csv` e `.html` pelo `reader` e
      devolve o mesmo texto que as nativas.
- [ ] Manifesto `api_version = 1` aparece como inválido, com o motivo, na
      área Plugins e no `check`.
- [ ] `_molde` do `xl_U-Plugins` passa no `check` com API 2.
- [ ] `ruff`, `pytest` e `uv run python scripts/check_docs.py` verdes.

## Orçamento de contexto (≤90 linhas)

`shared/plugins/api.py` e `controllers/plugins.py` (curtos);
`core/plugins/manifest.py` só a validação de `api_version`;
`core/tools/all_str.py` só `prepare_workbook`; `docs/plugins/api.md` →
**`PluginRequest`** e **Compatibilidade**.

## Arquivos prováveis

- `src/xl_utils/shared/plugins/api.py`, `controllers/plugins.py`
- `src/xl_utils/core/plugins/manifest.py`, `core/tools/all_str.py`
- `docs/plugins/*.md`, `docs/plugins/exemplos/*/plugin.toml`
- `tests/test_plugin_controller.py`, `test_plugin_manifest.py`,
  `test_plugin_examples.py`, `tests/plugin_helpers.py`

## Riscos

- Plugin instalado com API 1 fica inválido: a listagem tem de mostrar o
  motivo, não sumir com ele.
- Ler o arquivo inteiro a cada chamada pesa em lote: cachear por execução.
- Sem `pre_run` no `ToolLayout` (S19): aviso de reexecução fica com o plugin.

## Próximo depois desta

S21 — Menu de perfis do Drive sem troca de conta.
