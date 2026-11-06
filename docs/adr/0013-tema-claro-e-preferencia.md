# ADR 0013 — Tema claro e preferência salva

- **Status:** aceita
- **Data:** 2026-11-06

## Contexto

A paleta Dracula era um conjunto de constantes em `ui/theme.py`, lidas pelos
componentes no momento em que montavam cada controle. O dono pediu leitura
confortável em ambiente claro, sem mudar layout nem fluxo das ferramentas.
Trocar a paleta ao vivo exigiria reconstruir a árvore de controles e repetir
todo o estado da página, o que aumenta o risco sem entregar valor imediato.

## Decisão

- `ui/theme.py` guarda `DARK` e `LIGHT` com as mesmas chaves e expõe
  `apply(mode)`: ele troca os tokens do módulo. `build_theme(mode)` monta o
  `ColorScheme` direto da paleta pedida, sem depender do estado global.
- As paletas usam nomes semânticos (`TEXT`, `MUTED`, `SUBTLE_TEXT`,
  `CHIP_TEXT`, `SUCCESS_BG`, `SELECTED_BG`, `ICON_BG`, `SUCCESS_BORDER`) e os
  componentes leem `theme.X` ao montar o controle.
- `shared/settings.py` persiste a chave `theme` em
  `%LOCALAPPDATA%/xl_utils/settings.json`, com fallback para
  `~/.xl_utils/settings.json`. Gravação usa arquivo temporário e `os.replace`.
- `app.main` lê a preferência e chama `theme.apply` **antes** de montar a
  sidebar e o hub. `page.theme` recebe a paleta clara, `page.dark_theme` a
  escura, e `page.theme_mode` escolhe uma delas.
- A sidebar grava a escolha na hora e mostra “Reabra o aplicativo para
  aplicar”. Não há reconstrução da UI nem mudança ao vivo.

## Consequências

- A preferência sobrevive ao fechamento; settings ausente, corrompido ou com
  valor desconhecido cai no escuro sem erro visível.
- O tema só muda depois de reabrir o app. É a limitação aceita nesta fase.
- A paleta clara é a variante Alucard do Dracula: creme quente, sem branco
  puro, com os mesmos matizes escurecidos. Foi medida com contraste AA nos
  pares de texto, chips e status; o texto principal do tema escuro também passa.
  O `MUTED` escuro continua como estava para não alterar a identidade visual do
  Dracula.
- Nenhuma regra de ferramenta, recorte ou merge muda.
- `settings.json` guarda só preferências, nunca caminho de planilha ou
  conteúdo de célula.

## Alternativas

- **Troca ao vivo com reconstrução:** exigiria reidratar páginas e estado;
  fica fora de escopo até existir demanda.
- **Seguir o tema do Windows:** o resultado mudaria sem o usuário pedir;
  preferência explícita é mais previsível.
- **QSettings ou registry:** adiciona dependência/plataforma; JSON no
  `%LOCALAPPDATA%` é simples, portátil e testável.
