# Roadmap atual

Ciclo ativo: **0006 — Backlog**. O ciclo anterior está em
[`0005-polimento.md`](0005-polimento.md).

## Sessões

| Sessão | Entrega | Estado |
|---|---|---|
| S7a | Vinculação I — motor + AGENDA × PROCESSOS | [x] |
| S7b | Trocar nome de "Vincular Planilhas" para "Verificar Vínculos". | [x] |
| S7c | Vinculação II — FINANCEIRO + CLIENTES | [ ] |
| S7d | Vinculação III — campo único, log e acabamento | [ ] |
| S8 | Alinhamento de colunas em tela cheia no merge | [ ] |
| S9a | Drive I — ADR, OAuth, contas e shell | [ ] |
| S9b | Drive II — link/seletor e escrita do resultado | [ ] |
| S9c | Drive III — exportação nas demais e acabamento | [ ] |

Ordem definida pelo dono: **vinculação → tela cheia → Drive**. O Drive fica por
último porque muda o caminho de saída de todas as ferramentas; a S9 só vira
duas ou três sessões depois do ADR de autenticação.

## S7a — entregue

Motor puro em `core/tools/link.py`, duas entradas rotuladas (AGENDA e
PROCESSOS), `VINCULA?` e preservação do protocolo na descrição com
`MIGRAÇÃO`. A config empacotada nasceu em `src/xl_utils/configs/headers.json`
e o override por máquina em `%LOCALAPPDATA%/xl_utils/headers.json`. Detalhes na
[spec](../sessions/S7a-vinculacao-agenda.md) e nos ADRs 0014 e 0015.

## S7b — nome da ferramenta

“Vincular Planilhas” passa a se chamar **Verificar Vínculos** na sidebar, no
cabeçalho da página, no README e na referência. A descrição acompanha o novo
vocabulário. O `id` interno, os módulos e a regra de vinculação não mudam.

## S7c — FINANCEIRO e CLIENTES

Acrescenta as outras duas entradas rotuladas. No FINANCEIRO, `VINCULA?` usa a
mesma prioridade CNJ → PASTA → PROTOCOLO; `VINCULA (POR NOME)?` recebe
SIM/NÃO comparando o nome com a lista única de PROCESSOS (split por `;`) e
CLIENTES. A descrição usa `" | "` e o prefixo `NOME DO CLIENTE: X`. Opção
“nome sem vínculo na descrição”. Ver
[spec](../sessions/S7c-vinculacao-financeiro.md).

## S7d — acabamento da vinculação

Opção “manter apenas um campo vinculante” (AGENDA, FINANCEIRO ou ambos),
etapas no log, cartão no Início e revisão dos textos. Fecha a regra de
vinculação com um ADR de adendo, se necessário.

## S8 — tela cheia no merge

Botão maximizar ao lado de “Alinhamento de colunas”; a seleção ocupa a tela
inteira e restaura no mesmo botão ou em “CONFIRMAR”, exibido no canto inferior
direito só quando maximizado. Mantém a largura de cada card e usa toda a
largura para distribuí-los lado a lado, sem esticá-los. Não muda o modelo de
grupos.

## S9 — Google Drive

Duas entradas: link da planilha ou seletor de arquivos do Drive. Login pelo
navegador (OAuth), múltiplas contas e “sair” na tela inicial; menu hamburger
num dos cantos superiores. Antes do código, o ADR decide escopo, lib e destino
da saída (aba extra ou pasta `output` ao lado). S9a entrega só a autenticação;
S9b, a transferência; S9c, a exportação nas demais ferramentas.

## Backlog detalhado — vinculação

**Planilhas e campos.** Quatro planilhas padrão — AGENDA, CLIENTES, FINANCEIRO
e PROCESSOS — ligadas por NOME DO CLIENTE, CNJ, PROTOCOLO e PASTA. Os rótulos
reais vivem em `headers.json`; a comparação de cabeçalho dobra caixa, acento e
espaço, mas os valores das células são comparados como estão.

| Planilha | Vincula a | Campos |
|---|---|---|
| AGENDA | PROCESSOS | CNJ, PASTA e PROTOCOLO |
| CLIENTES | PROCESSOS, FINANCEIRO | NOME |
| FINANCEIRO | PROCESSOS, CLIENTES | CNJ, PASTA, PROTOCOLO e NOME |
| PROCESSOS | AGENDA, CLIENTES, FINANCEIRO | CNJ, PASTA, PROTOCOLO e NOME |

- **CNJ:** máscara canônica `NNNNNNN-NN.NNNN.N.NN.NNNN` ou 20 dígitos crus;
  qualquer outra forma preenchida interrompe tudo e lista os casos.
- **NOME:** valor único em CLIENTES e FINANCEIRO; em PROCESSOS, vários nomes na
  mesma célula separados por `;`.
- **Células vazias:** permitidas; se todos os campos estiverem vazios, não
  vincula.
- **Sem vínculo na AGENDA:** `NÃO vincula, apenas processo consultivo`, o
  protocolo vai para o fim da descrição e o campo vira `MIGRAÇÃO` — sempre.
- **Sem vínculo no FINANCEIRO:** não move protocolo nem usa `MIGRAÇÃO`.
- **Saída:** mesma lógica das demais ferramentas (`output/` ou pasta
  escolhida), preservando todas as colunas de entrada.

## Manutenção

- Rodar `uv lock --upgrade` no início do ciclo e validar pandas/Flet — critério:
  testes verdes e app abrindo.
- Revisar `docs:check` no CI a cada mudança de documentação.
- Atualizar o code tour quando um módulo do core mudar de papel.

## Gatilhos (não são backlog)

- Suporte a macOS/Linux — só entra quando houver máquina para testar.
- Empacotamento, instalador e release — só entram quando o dono decidir
  distribuir. A config já nasce pronta para o wheel.
- Internacionalização — só entra se aparecer usuário fora do PT-BR.
- Drag & drop real de arquivos — só entra se migrar para PySide6 ou houver hook
  Windows-only.

## Descartados (não voltam sem decisão nova)

- Histórico de execuções — descartado pelo dono ao fechar o ciclo 0004.
- CLI com `click` — a branch `cli-app` foi apagada; ver ADR 0001.
- `demoji` — incompatível com Python 3.15 e API removida; ver ADR 0001.
- Ferramentas `convert` (JSON → planilha) e `quick_replace` (substituir
  nomes) — saem sem substituto, conforme decisão do dono.
- Página própria de `remove_emoji` — a remoção de emojis entra no pipeline do
  `all_str`; ver ADR 0004.
- Renomear o arquivo original do usuário para “corrigir” extensão — proibido
  por design; a leitura usa o tipo real sem tocar no arquivo.
- Normalizar quebras de linha automaticamente — rejeitado; preservar o texto.
