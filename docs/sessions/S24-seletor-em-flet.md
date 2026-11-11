# S24 — Seletor de arquivos em Flet (implementação)

> **Backlog:** spec escrita na S15; não é a próxima sessão. Entra no ciclo 0010
> se o dono priorizar. O ADR 0025 tem a decisão e as medições.

## Objetivo

Trocar o diálogo nativo por um seletor de arquivos e pastas próprio, no tema,
com paginação, busca, filtro por formato e recentes, mantendo o seletor nativo e
o Picker do Drive como fallback.

## Fora de escopo

- Drive sem consentimento repetido (S16) e qualquer mudança de escopo OAuth.
- Migrar a stack ou embutir webview; o ADR 0025 preteriu os dois.
- Arrastar e soltar do sistema operacional; o Flet não expõe.

## Tarefas

1. `core/files.py` com listagem (`os.scandir`), filtro por extensão, ordenação
   (pastas primeiro), busca e store de recentes; funções puras e testáveis sem
   Flet.
2. Store de recentes em `%LOCALAPPDATA%/xl_utils/recent.json`, escrita atômica,
   no máximo dez caminhos com data; ignorar cache do Drive.
3. `ui/components/file_selector.py`: diálogo/overlay com breadcrumb, subir,
   busca, filtro, lista paginada (300), seleção e botão “Abrir”. Tamanho relativo
   à janela, testado em 100%, 125% e 150%.
4. Integrar ao `FileInput` como opção, mantendo o seletor nativo; a leitura de
   abas e o fluxo das ferramentas não mudam.
5. Testes: core (listagem, filtro, recentes), UI headless (paginação, seleção,
   fallback) e manual com 25.000 arquivos, pasta de rede/OneDrive, tema claro e
   escuro.
6. Atualizar `docs/reference/ui.md`, o code tour e o CHANGELOG.

## Aceite

- [ ] Seletor abre no tema, navega em pastas, filtra, busca e seleciona.
- [ ] Primeira página responde em menos de 1 s em pasta de 25.000 itens.
- [ ] Seletor nativo continua disponível e o Picker do Drive não muda.
- [ ] Recentes persistem entre execuções e não guardam caminho do cache.
- [ ] `ruff`, `pytest` e `node scripts/check-docs.mjs` verdes.

## Orçamento de contexto (≤90 linhas)

Ler o ADR 0025, `ui/components/file_input.py`, `ui/components/tool_layout.py`
→ entrada de arquivos, `docs/reference/ui.md` → **Entrada de arquivos** e
`docs/adr/0021-instalador-windows.md` só se o build for tocado.

## Arquivos prováveis

- `src/xl_utils/core/files.py`, `tests/test_files.py`
- `src/xl_utils/ui/components/file_selector.py`, `tests/test_file_selector.py`
- `src/xl_utils/ui/components/file_input.py`, `tests/test_file_input_drive.py`
- `docs/reference/ui.md`, `docs/guide/code-tour.md`, `CHANGELOG.md`

## Riscos

- Flet não virtualiza a lista no processo Python: nunca montar 10.000 linhas;
  paginar e listar em `asyncio.to_thread`.
- DPI e largura fixa cortam o diálogo; calcular a partir de `page.width`.
- Pastas de rede/OneDrive podem bloquear; tratar erro e não travar a UI.
- Recentes com caminho do cache do Drive apontam para arquivo que some no
  próximo início; filtrar `drive_cache.is_cached`.
- O seletor não substitui o nativo de imediato; validar antes de virar padrão.

## Próximo depois desta

Decidir se o seletor vira o padrão ou continua como opção; se virar, remover o
botão nativo da dropzone e manter o fallback no menu.
