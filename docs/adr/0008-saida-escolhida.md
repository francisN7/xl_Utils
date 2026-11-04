# ADR 0008 — Salvar só depois da escolha

- **Status:** aceita
- **Data:** 2026-11-04

## Contexto

Até a S2d, executar já gravava em `output/` antes de qualquer confirmação. O
usuário não escolhia o destino, um lote só cabia na pasta de cada origem e um
erro de escrita aparecia depois do arquivo já ter sido criado. A prévia exibida
era, na prática, um retrato de algo que já estava no disco.

## Decisão

- Os controllers param de gravar. Cada execução devolve `SaveItem` com
  `suggested_name`, as abas em memória e o `output/` da origem.
- `core/save.py` concentra a escrita:
  - `save_chosen(items, destino)` grava um item no arquivo escolhido ou vários
    itens na pasta escolhida; `None` (cancelamento) não grava nada;
  - `save_to_output(items)` mantém o atalho para o `output/` de cada origem;
  - `save_item` usa `save_workbook`/`unique_path` e embrulha falhas em
    `SaveError`.
- `ResultPanel` ganha o estado “Pronto para salvar” e dois botões: **Salvar**
  (seletor nativo) e **Salvar em output/** (atalho). Depois de gravar, mostra o
  caminho real, libera “Abrir pasta” e registra `Salvo: <caminho>` no log.
- `ToolLayout` guarda os `SaveItem` em `ToolState.save_items`, anexa o
  `ft.FilePicker` em `page.services` (como o `FileInput`) e chama a gravação em
  thread separada. Falha de escrita não apaga a prévia.
- Extensão de saída é sempre `.xlsx`; o nome sugerido é editável no diálogo.

## Consequências

- Executar não cria arquivo, pasta ou efeito colateral no disco.
- Cancelar o seletor é uma operação segura e sem exceção.
- Lote e várias partes usam uma pasta única escolhida; o atalho preserva a
  pasta de cada origem e o merge usa a primeira.
- Colisões de nome são resolvidas por `unique_path` e o log mostra o caminho
  real, não o sugerido.
- Testes de gravação não precisam de Flet: `core/save.py` é puro e recebe o
  caminho já escolhido.
- O diagnóstico continua sem conteúdo de célula; só nomes e caminhos entram.

## Alternativas

- **Gravar em `output/` e depois mover:** cria arquivo intermediário, falha no
  meio e deixa lixo; rejeitado.
- **Pedir o destino antes de executar:** impede calcular o nome e mostrar a
  prévia antes da escolha; rejeitado.
- **Sobrescrever o arquivo escolhido:** perde dados sem aviso; rejeitado em
  favor de sufixo automático.
- **Seletor próprio em Tkinter:** duplica o serviço nativo do Flet e quebra no
  tema; rejeitado.
