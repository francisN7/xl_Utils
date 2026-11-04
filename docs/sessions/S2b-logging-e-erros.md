# S2b — Logging e erros

## Objetivo

Cada execução gera um log estruturado e copiável; falhas mostram a causa tipada
e um diagnóstico completo no painel de resultado.

## Fora de escopo

Persistir histórico entre execuções (backlog); cancelar execução em andamento;
telemetria ou envio automático de diagnóstico; testes de widget.

## Tarefas

1. Criar `shared/log.py` com `RunLog`: lista ordenada de eventos
   `(nível, texto)`, helpers `info`, `success`, `warning` e `error`, e
   `to_text()` com uma linha por evento. Nada de `print`.
2. `ToolState` guarda `log: RunLog | None` e `error_detail: str | None`. O
   `ToolLayout` zera ambos ao trocar os arquivos.
3. Fazer os controllers registrarem no `RunLog` os mesmos passos de hoje
   (arquivo, tipo, abas, linhas, colunas e saída), preservando a ordem e a
   compatibilidade com `join_logs`/`prefixed_frames`.
4. `ResultPanel` ganha “Copiar diagnóstico” ao lado de “Copiar log”. O texto
   inclui: versão do app, Python, pandas e Flet; arquivos e abas selecionadas;
   opções da ferramenta; tipo, mensagem e causa do erro; traceback quando
   houver.
5. `ToolLayout._run` passa a distinguir `WorkbookReadError` (título “Não foi
   possível ler a planilha”) de `ValueError` (título “Confira a seleção”) e de
   falhas inesperadas; guarda o traceback em `ToolState` e mostra o detalhe no
   painel, sem esconder a mensagem original.
6. Criar `tests/test_log.py`: ordem dos eventos, texto final, diagnóstico com
   versões, arquivos, abas, opções, causa e traceback; ausência de campos
   vazios quando não há erro.
7. Atualizar `reference/architecture.md` (logging/erros), `reference/ui.md`
   (painel e estados), `CURRENT.md`, roadmap e `CHANGELOG.md`.

## Aceite

- [x] toda execução produz um log com passos e resultado final
- [x] erro mostra título amigável, mensagem original e causa
- [x] “Copiar diagnóstico” gera texto com versões, entrada, opções e traceback
- [x] log e diagnóstico continuam funcionando no lote e no merge
- [x] `ruff`, `pytest` e `docs:check` verdes

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec,
`reference/architecture.md` (Leitura segura, Saída), `reference/ui.md`
(Resultado e Estados), `shared/system.py`, `ui/components/result_panel.py`,
`ui/components/tool_layout.py`, `ui/state.py` e os controllers só pelas
assinaturas.

## Arquivos prováveis

- `src/xl_utils/shared/log.py`
- `src/xl_utils/ui/state.py`
- `src/xl_utils/ui/components/result_panel.py`
- `src/xl_utils/ui/components/tool_layout.py`
- `src/xl_utils/controllers/*.py`
- `tests/test_log.py`

## Riscos

- Trocar `list[str]` por `RunLog` quebra `join_logs`; manter a interface ou
  adaptar os helpers em `ui/pages/batch.py`.
- Traceback e caminhos locais no clipboard são esperados, mas não incluir
  valores de células nem conteúdo de planilha.
- Versões vêm de `importlib.metadata`; o pacote pode não estar instalado em
  testes — usar fallback “desconhecida”.
- Falha ao copiar no clipboard não pode derrubar a execução.
- Diagnóstico muito longo: limitar o traceback e manter o texto selecionável.

## Próximo depois desta

S2c — opções reais ou nada: remover os checkboxes desabilitados de Texto e CNJ e
só mostrar “2. Opções” quando houver algo editável.
