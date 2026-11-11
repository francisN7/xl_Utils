# ADR 0025 — Seletor de arquivos próprio em Flet

**Status:** aceita, com adendo · **Data:** 2026-11-11 · **Contexto:** ciclo 0009, S15

## Contexto

Hoje cada ferramenta abre o diálogo nativo do Windows (`ft.FilePicker`) e, no
Drive, o Picker do Google em uma aba do navegador. Os dois saem do visual e do
fluxo da janela: o nativo não segue o tema, o do Drive exige consentimento e
troca de contexto. O dono quer um seletor de arquivos e pastas dentro do app,
com filtro por formato e recentes, sem perder o seletor nativo como fallback.

A decisão precisa considerar o que o Flet 1.1.2 oferece, o empacotamento do
Windows (ADR 0021), o login do Drive (ADR 0018) e o custo de trocar a stack
(ADR 0001). A S15 mediu um spike descartável antes de recomendar a
implementação.

## Decisão

- **Caminho A: seletor em Flet puro, dentro de um diálogo/overlay do app.** O
  processo Python lê o disco com `os.scandir`; a UI monta a lista no tema.
- **Não migrar a stack e não embutir webview nesta decisão.** O Flet 1.1.2 não
  expõe `WebView`; a alternativa B exigiria extensão Flutter, ponte Python/JS e
  um novo risco de empacotamento. A alternativa C (PySide6) reescreveria toda a
  UI e o instalador.
- **Paginação obrigatória.** A primeira página tem no máximo 300 itens; o botão
  “Carregar mais” acrescenta mais 300. O Flet não virtualiza a árvore de
  controles no lado Python: 5.000 `ListTile` já custam ~10 MB e ~500 ms.
- **Listagem fora da UI thread.** `os.scandir`, filtro e ordenação rodam em
  `asyncio.to_thread`; a UI recebe o resultado e atualiza na thread do Flet.
- **Recentes locais em disco.** `%LOCALAPPDATA%/xl_utils/recent.json`, no máximo
  dez caminhos com data; nada de conteúdo de célula. Cópias temporárias do
  Drive não entram nos recentes; o Drive continua no Picker até a S16 decidir
  outro pipeline.
- **Fallback preservado.** O botão “Seletor nativo” abre o `FilePicker` atual e
  o fluxo do Drive não muda. Nenhuma ferramenta troca de comportamento nesta
  sessão; o spike é descartável e não entra no pacote.
- **Tamanho relativo à janela.** O diálogo calcula largura/altura a partir de
  `page.width`/`page.height`, com limites, e é testado em 100%, 125% e 150% de
  escala. Um valor fixo de 820 px cortou o conteúdo em 125% no spike.

## Evidências

Ambiente: Windows 11 Pro 25H2, AMD Ryzen 5 5500U, 8 GB, Flet 1.1.2, Python
3.15, tela 1920×1080 a 125%. Pasta fictícia com 25.000 entradas (`.xlsx`,
`.csv`, `.html`, vazias), mais uma subpasta.

| Medição | Resultado |
|---|---|
| `os.scandir` + filtro + ordenação (25.000 itens) | mediana **110,0 ms** (7 amostras; 106,3–121,3 ms) |
| `Path.iterdir` + `is_dir` (10.000 itens) | **124,9 ms**; `os.scandir` no mesmo teste: **46,1 ms** |
| Montar 100 `ListTile` | 7,1 ms |
| Montar 500 `ListTile` | 44,6 ms |
| Montar 1.000 `ListTile` | 86,7 ms · pico **1,9 MB** |
| Montar 5.000 `ListTile` | 501,7 ms · pico **9,8 MB** |
| Abrir a pasta de 25.000 com a primeira página de 300 | **420,7 ms** no spike (listagem + 300 linhas + `page.update`) |
| Cliente Flet em execução | ~143 MB de working set; o processo Python do spike, ~8 MB |

O spike abriu o diálogo no tema, listou a subpasta e os arquivos, filtrou por
extensão, mostrou recentes e implementou a seleção com o botão “Abrir”. A
captura usada como evidência fica em `artifacts/spike_selector/` (ignorada pelo
Git; contém caminho pessoal e não é publicada).

## Alternativas

| Critério | A — Flet puro | B — Webview/HTML | C — PySide6 |
|---|---|---|---|
| Consentimento | nenhum para arquivo local; Drive segue o Picker da S16 | poderia usar Picker web, mas exige API key, verificação e ponte | nenhum para local; Drive igual |
| Tema | total, mesmos tokens da sidebar e das ferramentas | HTML pode imitar, mas o controle não existe no Flet 1.1.2 | total, porém reescrevendo o tema atual |
| Filtros | fáceis: `os.scandir` + sufixo + busca | fáceis em JS, difíceis de atravessar a ponte | fáceis no modelo Qt |
| Recentes | store próprio ou pasta Recent do Windows | store próprio/JS | store próprio |
| Esforço | médio; 1–2 sessões | alto; extensão Flutter, ponte e empacotamento | muito alto; migração de toda a UI |
| Risco | lista não virtualizada, DPI, rede/OneDrive | segurança da ponte, build e consentimento | regressão ampla, ADR 0001 e instalador |

## Consequências

- A implementação fica no app, sem dependência nova e sem mudar o instalador.
- O seletor não substitui o nativo de imediato: entra como opção e só vira
  padrão depois de validar pastas de rede, OneDrive e escala de tela.
- O usuário ganha filtro por formato, busca, recentes e navegação de pastas no
  tema; perde, por enquanto, arrastar e soltar (o Flet não expõe).
- A pasta grande continua responsiva porque a listagem sai da UI thread e a
  lista é paginada; a primeira página de 300 é o limite acordado.
- O Drive não é afetado: arquivos do Drive continuam vindo pelo Picker e pelo
  cache local da ADR 0018.

## Implementação recomendada

1. `core/files.py` (ou equivalente) com funções puras de listagem, filtro,
   ordenação e recentes, testadas sem Flet.
2. `ui/components/file_selector.py` com o diálogo, paginação, busca, filtro e
   fallback nativo; o `FileInput` ganha o botão de abrir o seletor.
3. Store de recentes em `%LOCALAPPDATA%/xl_utils/recent.json`, com escrita
   atômica e limite; sem caminhos do cache do Drive.
4. Testes de core, de UI headless e um teste manual com 25.000 arquivos, pasta
   de rede/OneDrive, tema claro/escuro, 100%/125%/150%.
5. Só então avaliar tornar o seletor o padrão; o nativo e o Picker continuam
   como fallback em qualquer caso.

## Adendo — 2026-11-11

O dono restringiu o escopo: **o seletor interno é exclusivo da rota do Drive**.
Arquivo local continua sempre no seletor nativo do sistema operacional; não há
plano de substituí-lo. Isso corrige a leitura das seções acima:

- O spike com `os.scandir` provou a **viabilidade da UI em Flet** e o custo de
  paginação; ele não define a fonte de dados do seletor definitivo. A lista do
  Drive virá da Drive API, com o pipeline decidido na S16/ADR 0026.
- `core/files.py` e o store de recentes locais saem do escopo. Entram a
  listagem de pastas/arquivos do Drive, a paginação por `nextPageToken`, o
  cache local da ADR 0018 e os erros de token/permissão.
- O seletor só entra na rota do Drive; o `FileInput` local permanece intocado.
  A implementação foi reescopada na spec `docs/sessions/S24-seletor-do-drive.md`.
- A decisão de viabilidade da UI (Flet puro, paginação, tema) continua válida;
  o que muda é o dado que alimenta a lista.

