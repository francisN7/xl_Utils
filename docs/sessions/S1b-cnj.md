# S1b — Extração de CNJ

## Objetivo

Extrair, padronizar e deduplicar numerações CNJ de todas as abas de uma
planilha, usando o pipeline do `all_str`, e entregar a lista em `output/`.

## Fora de escopo

Migrar `cut` ou `merge`; validar dígitos verificadores do CNJ; editar a
planilha de origem; caçar CNJ fora dos padrões aceitos.

## Tarefas

1. Criar `core/tools/cnj.py` com funções puras:
   - `extract_cnjs(text)` aceita o formato pontuado
     (`NNNNNNN-DD.AAAA.J.TR.OOOO`) ou 20 dígitos seguidos;
   - `normalize_cnj(value)` devolve o formato pontuado;
   - `collect_cnjs(sheets)` percorre todas as células e devolve a lista
     ordenada e sem duplicatas.
2. Ler sempre por `all_str.prepare_workbook`; nenhum CNJ deve vir de célula
   ainda com emoji.
3. Criar `controllers/cnj.py` que grava
   `output/<nome> lista cnj.xlsx` com uma coluna `PROCESSOS` e devolve caminho,
   lista e log (abas lidas, encontrados, duplicados removidos).
4. Conectar a página “Extrair CNJs” ao run handler, com opções fixas
   (padronizar e remover duplicados) e resultado com caminho, log e prévia.
5. Criar `tests/test_cnj.py`: formato pontuado, 20 dígitos, texto no meio de
   frase, duplicatas entre abas, célula vazia e planilha sem CNJ.
6. Apagar `cnjs.py` da raiz.
7. Atualizar `CURRENT.md`, roadmap, `CHANGELOG.md` e
   `reference/architecture.md`.

## Aceite

- [ ] CNJ de 20 dígitos e CNJ pontuado saem no mesmo formato
- [ ] duplicatas entre abas são removidas e o log informa a contagem
- [ ] planilha sem CNJ termina com lista vazia e mensagem clara, sem erro
- [ ] a página executa, salva em `output/` e mostra caminho, log e prévia
- [ ] `ruff`, `pytest` e `docs:check` verdes
- [ ] `cnjs.py` removido da raiz

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec,
`docs/reference/architecture.md` e `core/tools/all_str.py`. Consultar
`controllers/all_str.py`, `ui/pages/all_str.py` e `cnjs.py` só para copiar o
padrão; não abrir os outros scripts legados.

## Arquivos prováveis

- `src/xl_utils/core/tools/cnj.py`
- `src/xl_utils/controllers/cnj.py`
- `src/xl_utils/ui/pages/cnj.py`
- `src/xl_utils/ui/pages/registry.py`
- `tests/test_cnj.py`

## Riscos

- Regex frouxa demais captura CPF/telefone; exigir 20 dígitos ou o padrão
  pontuado completo.
- `astype(str)` em célula vazia gera `"nan"`; filtrar antes de procurar.
- Pandas converte colunas numéricas; por isso o pipeline `dtype=str` é
  obrigatório antes do regex.
- Planilha grande: evitar regex por célula repetida; compilar uma vez.

## Próximo depois desta

S1c — migrar `cut` (recorte por quantidade de linhas).
