# S15 — Seletor de arquivos integrado à UI (investigação)

> **Resultado:** o seletor interno é só para a rota do Drive; arquivo local
> continua no seletor nativo. O adendo do ADR 0025 corrige o escopo e a
> implementação foi reescopada para a S24.

## Objetivo

Medir, com protótipo descartável, se o app consegue ter um seletor de arquivos
e pastas próprio — no tema e dentro da janela — e registrar a decisão no ADR
0025, mantendo o seletor nativo e o Picker como fallback.

## Fora de escopo

- Migrar a stack para PySide6 ou webview nesta sessão; só medir o custo.
- Entregar o seletor definitivo ou mudar o fluxo de entrada das ferramentas.
- Drive sem consentimento repetido (S16) e release 0.4.0.

## Tarefas

1. Inventariar o que o Flet 1.1.2 oferece hoje para listar diretórios, filtrar
   por extensão, abrir arquivo e hospedar conteúdo próprio (serviços, janela,
   webview) sem sair do tema.
2. Comparar três caminhos com esforço e risco: (A) seletor em Flet puro lendo o
   disco no processo; (B) webview embutida com seletor HTML; (C) PySide6 ou
   outra stack. Considerar empacotamento (ADR 0021), DPAPI/Drive (ADR 0018) e
   autorização do Windows.
3. Construir um spike descartável do caminho mais promissor: listar pastas,
   filtro por formato, recentes e seleção; sem integrar às ferramentas.
4. Medir abertura, navegação em pasta grande e memória; testar no Windows 11
   com planilhas fictícias.
5. Escrever o ADR 0025 com a tabela (consentimento, tema, filtros, recentes,
   esforço, risco) e a recomendação; atualizar `docs/reference/ui.md` e o
   backlog do roadmap.
6. Se a decisão for "sim", escrever a spec da implementação; se for "não",
   registrar o motivo e descartar o spike.

## Aceite

- [ ] ADR 0025 aceito, com tabela comparativa e evidências das medições.
- [ ] Fluxo padrão intacto: seletor nativo e Picker continuam funcionando.
- [ ] Spike removido ou atrás de flag desligada; nada muda por padrão.
- [ ] `ruff`, `pytest` e `node scripts/check-docs.mjs` verdes.
- [ ] Backlog e `docs/reference/ui.md` refletem a decisão.

## Orçamento de contexto (≤90 linhas)

Ler o ADR 0025 (quando existir), `ui/components/file_input.py`, `ui/drive.py`,
`docs/reference/ui.md` → **Entrada de arquivos** e os ADRs 0001, 0003, 0018 e
0021. Abrir a documentação do Flet só para a API em teste; não reler o core.

## Arquivos prováveis

- `docs/adr/0025-seletor-de-arquivos.md`, `docs/adr/README.md`
- `docs/reference/ui.md`, `docs/roadmap/main.md`, `docs/sessions/`
- spike em pasta descartável (não entra no pacote)

## Riscos

- O Flet 1.1 pode não expor listagem de diretório; nesse caso o caminho B ou C
  vira o custo real e o ADR precisa dizer isso com números.
- Webview/PySide6 mexe no empacotamento e no instalador; não prometer migração
  sem validar o build.
- Spike grande demais vira implementação escondida; limitar a uma pasta e um
  diálogo, sem tocar em `ToolLayout`.
- Medição em máquina única não generaliza: registrar o ambiente junto.

## Próximo depois desta

S16 — Drive sem consentimento repetido; ou a release 0.4.0, se o dono
priorizar o empacotamento antes.
