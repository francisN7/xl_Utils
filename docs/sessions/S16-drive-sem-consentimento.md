# S16 — Drive sem consentimento repetido (investigação)

## Objetivo

Medir, com spike descartável, se o app consegue listar e escolher arquivos e
pastas do Drive com o token do login — sem abrir o Picker e sem repetir o
consentimento — e registrar a decisão no ADR 0026, mantendo o fluxo atual como
fallback.

## Fora de escopo

- Trocar o escopo OAuth ou publicar uma versão com o novo pipeline nesta sessão.
- Implementar o seletor do Drive (ADR 0025/S24), a release 0.4.0 ou a API 2
  dos plugins.
- Mexer na conta ativa, no menu de perfis (S21) ou na gravação de resultados.

## Tarefas

1. Inventariar o fluxo atual: `drive.file`, Picker de desktop, `prompt=consent`,
   concessão de pasta, tokens no DPAPI, cache local e gravação. Ler o ADR 0018,
   `shared/drive*.py`, `ui/drive.py` e `ui/components/file_input.py`.
2. Comparar quatro caminhos com esforço e risco: (A) Picker + `drive.file` como
   está; (B) Picker web com API key e webview embutida; (C) escopo `drive` com
   listagem própria usando o token do login; (D) outro navegador/OAuth próprio.
   Considerar verificação do Google, escopo restrito, acesso mínimo, revogação,
   multi-conta, DPAPI e empacotamento (ADR 0021).
3. Construir um spike descartável do caminho mais promissor: listar pastas e
   arquivos, filtrar por planilha, paginar e devolver o `file_id`; sem gravar e
   sem integrar às ferramentas.
4. Medir latência, número de chamadas, paginação e memória com uma conta real
   de teste, além do comportamento quando o token expira ou falta permissão.
5. Escrever o ADR 0026 com a tabela (consentimento, escopo, verificação,
   listagem, esforço, risco) e a recomendação; atualizar `docs/reference/ui.md`,
   `architecture.md` e o backlog do roadmap.
6. Se a decisão for “sim”, atualizar a spec `S24-seletor-do-drive.md` com o
   pipeline escolhido; se for “não”, registrar o motivo e descartar o spike.

## Aceite

- [ ] ADR 0026 aceito, com tabela comparativa e evidências das medições.
- [ ] Fluxo atual intacto: Picker, `drive.file`, cache e gravação continuam.
- [ ] Spike removido ou atrás de flag desligada; nada muda por padrão.
- [ ] `ruff`, `pytest` e `node scripts/check-docs.mjs` verdes.
- [ ] Backlog, `reference/ui.md` e `architecture.md` refletem a decisão.

## Orçamento de contexto (≤90 linhas)

Ler o ADR 0018, `shared/drive.py`, `drive_auth.py`, `drive_pick.py`,
`drive_store.py`, `ui/drive.py`, `ui/components/file_input.py`,
`docs/reference/ui.md` → **Entrada de arquivos** e `architecture.md` → **Drive**.
Abrir a documentação do Google/Flet só para o caminho em teste; não reler o core.

## Arquivos prováveis

- `docs/adr/0026-*.md`, `docs/adr/README.md`
- `docs/reference/ui.md`, `reference/architecture.md`, `docs/roadmap/main.md`
- spike em pasta descartável (não entra no pacote)

## Riscos

- Escopo `drive` é restrito e pode exigir verificação do Google; não prometer
  publicação sem medir o custo.
- Picker web depende de API key, origem autorizada e webview; o Flet 1.1.2 não
  tem `WebView`.
- Token expirado, conta sem permissão e pasta compartilhada são caminhos de erro
  que precisam de mensagem clara, não de traceback.
- Medição com uma conta não generaliza: registrar conta de teste, região e
  limites de cota.
- Spike grande demais vira implementação escondida; limitar à listagem e à
  escolha do `file_id`, sem tocar em `ToolLayout`.

## Próximo depois desta

S17 — ícone da sidebar e da janela; depois S18–S23 até a release 0.4.0.
