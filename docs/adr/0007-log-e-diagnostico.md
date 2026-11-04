# ADR 0007 — Log estruturado e diagnóstico copiável

- **Status:** aceita
- **Data:** 2026-11-04

## Contexto

Cada ferramenta gravava um log como `list[str]` e o painel só sabia copiar esse
texto. Quando uma leitura falhava, a UI mostrava “Falha ao executar” e a mensagem
crua, sem separar erro de planilha, seleção inválida ou defeito inesperado. Para
apoiar o usuário sem pedir acesso à máquina dele, o diagnóstico precisa caber no
clipboard: versões, entrada, opções e traceback, sem conteúdo de células.

## Decisão

- `shared/log.py` define `RunLog`, uma sequência ordenada de eventos
  `(nível, texto)` com helpers `info`, `success`, `warning` e `error`. `to_text()`
  renderiza `[INFO]`, `[OK]`, `[AVISO]` e `[ERRO]`; a iteração devolve as linhas,
  então os helpers antigos que esperavam `list[str]` continuam funcionando.
- `ToolState.log` guarda a execução atual; `ToolState.select_files` e `reset`
  zeram log e `error_detail`.
- Os controllers registram os mesmos passos de antes (arquivo, tipo, abas,
  linhas, colunas e saída) e devolvem `RunLog` nos outcomes; `join_logs` apenas
  concatena eventos, com linha em branco entre arquivos.
- `ToolLayout._run` classifica a falha em `WorkbookReadError` (“Não foi possível
  ler a planilha”), `ValueError` (“Confira a seleção”) e inesperada. A mensagem
  original fica visível; o traceback vai para `error_detail` e para o log.
- “Copiar diagnóstico” usa `build_diagnostics`, que inclui versões do app,
  Python, pandas e Flet, arquivos, abas selecionadas, opções, resultado e, quando
  houver, tipo, mensagem, causa e traceback limitado a 4.000 caracteres.

## Consequências

- O log deixa de ser só texto: níveis ficam disponíveis para testes e futuros
  filtros, sem quebrar a exibição atual.
- Versões vêm de `importlib.metadata`; ambiente de teste sem o pacote instalado
  mostra “desconhecida” em vez de falhar.
- Caminhos locais entram no diagnóstico por decisão explícita. Valores de
  células e conteúdo de planilha ficam de fora.
- Falha ao copiar para o clipboard é silenciosa e não derruba a execução.
- Diagnosticar um lote interrompido mostra os passos já concluídos e o erro que
  interrompeu o restante.

## Alternativas

- **Manter só `list[str]`:** não permite nível nem distinguir passos de falhas;
  rejeitado.
- **Gravar log em arquivo automaticamente:** cria artefato e histórico fora do
  escopo; fica no backlog de histórico de execuções.
- **Enviar diagnóstico por telemetria:** contraria a privacidade e o escopo
  offline; rejeitado.
- **Incluir prévia de células no diagnóstico:** pode vazar dados reais;
  rejeitado.
