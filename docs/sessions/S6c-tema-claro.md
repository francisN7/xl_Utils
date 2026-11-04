# S6c — Tema claro opcional

## Objetivo

Permitir escolher entre o tema Dracula (escuro) e um tema claro; a preferência
fica salva e é aplicada na próxima abertura do app.

## Fora de escopo

Troca ao vivo, seguir o tema do Windows automaticamente, temas de terceiros,
mudar layout ou tipografia, contraste AAA, empacotamento.

## Tarefas

1. Em `ui/theme.py`, separar os tokens em `DARK`/`LIGHT` e expor `apply(mode)`,
   que define o conjunto ativo antes da UI ser montada; `build_theme(mode)` usa
   a paleta ativa no `ColorScheme`. Os componentes continuam lendo
   `theme.BACKGROUND`, `theme.TEXT`, etc.
2. Definir a paleta clara com contraste AA e equivalentes para fundo, fundo
   profundo, superfície, borda, texto, muted, primária, destaque, sucesso,
   aviso, erro, info e os fundos de status. Registrar os tokens em
   `reference/ui.md` na mesma tabela do Dracula.
3. Criar `shared/settings.py` com leitura e escrita atômica de
   `%LOCALAPPDATA%/xl_utils/settings.json` (fallback `~/.xl_utils`), chave
   `theme` com `dark`/`light`. Arquivo ausente, inválido ou com valor
   desconhecido volta ao escuro sem erro visível.
4. Em `app.py`, ler a preferência **antes** de montar a sidebar e o conteúdo e
   aplicar `page.theme_mode` e `page.theme` correspondentes.
5. Na sidebar, adicionar um botão “Tema claro”/“Tema escuro” que grava a
   preferência e mostra um aviso “Reabra o aplicativo para aplicar”; não tentar
   reconstruir a UI ao vivo.
6. Cobrir settings (ida e volta, JSON corrompido, valor inválido), paletas
   (tokens e `build_theme` nos dois modos) e o carregamento no app; fazer smoke
   manual das telas Início e de uma ferramenta nos dois temas.

## Aceite

- [ ] a preferência sobrevive ao fechamento e é aplicada na abertura
- [ ] trocar na sidebar salva e pede reabertura; nada muda ao vivo
- [ ] os dois temas mantêm contraste AA e todos os estados legíveis
- [ ] settings ausente/corrompido cai no escuro sem derrubar o app
- [ ] nenhuma regra de ferramenta ou de recorte/merge muda
- [ ] `ruff`, `ruff format --check`, `pytest` e `docs:check` verdes

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec, `ui/theme.py`, `app.py`,
`ui/components/sidebar.py`, `ui/components/tool_layout.py` (só os tokens usados),
`reference/ui.md` (seções “Layout” e “Tema”), e `shared/system.py`.

## Arquivos prováveis

- `src/xl_utils/ui/theme.py`
- `src/xl_utils/shared/settings.py` (novo)
- `src/xl_utils/app.py`, `src/xl_utils/ui/components/sidebar.py`
- `tests/test_settings.py`, `tests/test_theme.py`
- `docs/reference/ui.md`, `docs/guide/code-tour.md`

## Riscos

- Componentes que importam a constante diretamente (`from ...theme import TEXT`)
  ignorariam a troca; confirmar que todos usam `theme.X`.
- Ler a preferência depois de `build_theme` deixaria o app sempre no escuro;
  aplicar antes de qualquer controle.
- A paleta clara precisa manter legíveis log, prévia, chips e estados
  sucesso/erro; validar não só o fundo principal.
- Escrita de settings não pode rodar no caminho de execução da ferramenta, só
  no clique do botão.
- Não gravar caminho absoluto nem conteúdo de planilha em `settings.json`.

## Próximo depois desta

Fechar o ciclo 0005 (provavelmente com esta única sessão) e reavaliar o backlog.
