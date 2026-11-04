# S2e — Saída escolhida após a prévia

## Objetivo

Executar sem gravar automaticamente, mostrar a prévia e só salvar quando o
usuário clicar em “Salvar”, escolhendo o arquivo (saída única) ou a pasta
(lote).

## Fora de escopo

Histórico de execuções; cancelar uma execução em andamento; outros formatos de
saída além de `.xlsx`; upload/nuvem; alterar o fluxo de entrada.

## Tarefas

1. Separar cálculo e gravação nos controllers: `run_*` devolve os dados em
   memória e um nome sugerido por saída, sem criar `output/` nem escrever.
2. Criar um modelo de saída compartilhado, por exemplo `SaveItem` com
   `suggested_name` e `sheets: dict[str, DataFrame]`, e uma função de gravação
   que recebe o caminho escolhido.
3. `ResultPanel` ganha o estado “Pronto para salvar” e os botões:
   - **Salvar** — saída única abre `FilePicker.save_file` com o nome sugerido;
   - **Salvar** com várias saídas abre `FilePicker.get_directory_path` e grava
     todas na pasta escolhida;
   - **Salvar em output/** como atalho, mantendo o comportamento atual de
     gravar no `output/` da origem (merge usa a primeira origem).
4. Gravar só depois da escolha; cancelar o seletor mantém a prévia e não cria
   nenhum arquivo. Não sobrescrever em silêncio: usar `unique_path` e mostrar o
   nome real no log.
5. Após salvar, exibir o caminho, liberar “Abrir pasta” e registrar no log
   `Salvo: <caminho>`; falha de escrita vira erro tipado sem perder a prévia.
6. Ajustar as páginas e o `ToolLayout` para guardar os `SaveItem`, chamar o
   seletor e repassar o resultado ao painel. O seletor nativo deve ser anexado
   como serviço da página, como já acontece no `FileInput`.
7. Criar testes para: controllers sem escrita, gravação em arquivo único,
   gravação em pasta, nomes livres, cancelamento e origem intacta.
8. Atualizar `reference/architecture.md` (Saída), `reference/ui.md`
   (Resultado), `CURRENT.md`, roadmap e `CHANGELOG.md`.

## Aceite

- [ ] executar não cria arquivo nenhum; a prévia aparece primeiro
- [ ] “Salvar” grava no local escolhido, com o nome sugerido editável
- [ ] lote ou várias partes escolhem uma pasta e gravam todas as saídas
- [ ] cancelar o seletor não grava e não apaga a prévia
- [ ] nomes existentes recebem sufixo e o log mostra o caminho real
- [ ] “Salvar em output/” continua disponível como atalho
- [ ] `ruff`, `pytest` e `docs:check` verdes

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec, `reference/architecture.md`
(Saída), `reference/ui.md` (Resultado), `core/io.py`, `core/paths.py`,
`ui/components/result_panel.py`, `ui/components/tool_layout.py`,
`ui/components/file_input.py`, as páginas e os controllers só pelas assinaturas.

## Arquivos prováveis

- `src/xl_utils/controllers/*.py`
- `src/xl_utils/ui/components/result_panel.py`
- `src/xl_utils/ui/components/tool_layout.py`
- `src/xl_utils/ui/pages/*.py`
- `src/xl_utils/shared/` ou `core/io.py` para a gravação
- `tests/test_save.py`

## Riscos

- Lote com saídas em pastas diferentes: decidir entre uma pasta única escolhida
  e o atalho por origem; documentar a diferença.
- `save_file`/`get_directory_path` são assíncronos e podem retornar `None`;
  tratar cancelamento sem exceção.
- O `FilePicker` só funciona anexado à página; em teste puro, separar a escolha
  do caminho da gravação.
- `save_workbook` já cria nomes livres; não duplicar a lógica de sufixo.
- A prévia atual mostra até 100 linhas; não confundir prévia com o arquivo
  completo na hora de salvar.
- Testes atuais esperam arquivos em `output/`; atualizar sem perder a cobertura
  de origem intacta.

## Próximo depois desta

Nenhuma sessão definida. Distribuição, instalador e release ficam fora do
roadmap até o dono decidir.
