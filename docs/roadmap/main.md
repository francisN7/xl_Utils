# Roadmap atual

Ciclo ativo: **0005 — Polimento**. O ciclo anterior está em
[`0004-execucao-e-robustez.md`](0004-execucao-e-robustez.md).

## Fase 1 — Execução visível

Objetivo: mostrar o que cada ferramenta está fazendo durante a execução e
separar a origem da linha na mesclagem.

- [x] **S6a — Mesclagem com `ORIGEM` e `LINHA_ORIGEM`.** `ORIGEM` passa a ser
  `<stem> - <aba>` e `LINHA_ORIGEM` numera as linhas do resultado inteiro com
  zeros à esquerda. Ver adendo do ADR 0005.
- [x] **S6b — Progresso e log por estágio.** As quatro ferramentas registram
  leitura, planilha carregada e cálculo no log ao vivo; a barra fica
  indeterminada durante cada arquivo e avança ao concluí-lo. Ver adendo do
  ADR 0011.

## Fase 2 — Aparência

Objetivo: permitir leitura confortável em ambiente claro sem mudar o layout nem
o fluxo das ferramentas.

- [ ] **S6c — Tema claro opcional.** Tokenizar as cores hoje constantes,
  alternar entre Dracula e claro e manter a preferência do usuário. A troca é
  aplicada ao reabrir o app. Custo M. Ver spec.

## Backlog

| Item | Valor | Custo | Pré-requisito |
|---|---|---|---|
| **Vinculação entre AGENDA, CLIENTES, FINANCEIRO e PROCESSOS** | Alto | G | Preencher `VINCULA?` em AGENDA e `VINCULA?` + `VINCULA (POR NOME)?` em FINANCEIRO, cruzando as quatro planilhas por CNJ, PASTA, nome e PROTOCOLO. Ver detalhe abaixo |
| Alinhamento de colunas em tela cheia (mesclar) | Alto | M | Botão maximizar ao lado de “Alinhamento de colunas”; a seleção ocupa a tela inteira; restaurar no mesmo botão ou em “CONFIRMAR”, exibido no canto inferior direito só quando maximizado. Mantém a largura de cada card e usa toda a largura da tela para distribuí-los lado a lado, sem esticá-los. Não muda o modelo de grupos |
| Envio direto do Google Drive (link ou seletor) | Alto | G | Duas entradas: link da planilha ou seletor de arquivos do Drive. Vem junto o login pelo navegador (OAuth), com suporte a múltiplas contas e opção de “sair” na tela inicial; o menu hamburger fica num dos cantos superiores, na posição que ficar melhor. Decidir antes de começar: quais ferramentas exportam local, quais gravam direto no link e, no caso do link, se o resultado vai numa aba extra da mesma planilha ou numa pasta `output` ao lado. Exige ADR de autenticação/escopo e escolha da lib de Drive API |

### Detalhe: vinculação

**Planilhas e campos.** Quatro planilhas padrão — AGENDA, CLIENTES, FINANCEIRO e
PROCESSOS — ligadas por NOME DO CLIENTE, N° DE CNJ, PROTOCOLO e PASTA; os nomes
das colunas variam. Prioridade de vínculo: 1) CNJ, 2) PASTA, 3) NOME DO
CLIENTE, 4) PROTOCOLO.

| Planilha | Vincula a | Campos |
|---|---|---|
| AGENDA | PROCESSOS | CNJ, PROTOCOLO e PASTA |
| CLIENTES | PROCESSOS, FINANCEIRO | NOME DO CLIENTE |
| FINANCEIRO | PROCESSOS, CLIENTES | CNJ, PROTOCOLO, PASTA e NOME |
| PROCESSOS | AGENDA, CLIENTES, FINANCEIRO | CNJ, PROTOCOLO, PASTA e NOME |

- **NOME DO CLIENTE:** múltiplos valores por célula em PROCESSOS, separados por
  `;`; valor único em CLIENTES e FINANCEIRO.
- **N° DE CNJ:** valor único, formato CNJ com máscara.
- **PROTOCOLO e PASTA:** valor único, campo livre.
- Células vazias são permitidas; se todos os campos estiverem vazios, não
  vincula.

**Saída em AGENDA.** Nova coluna `VINCULA?`. Testa CNJ → PASTA → PROTOCOLO e
para no primeiro vínculo, gravando `VINCULA POR CNJ`, `VINCULA POR PASTA` ou
`VINCULA POR PROTOCOLO`. Sem vínculo: `NÃO vincula, apenas processo
consultivo`; se houver protocolo, ele vai para o fim da descrição e no lugar
entra `MIGRAÇÃO` (sem isso a migração vira comentário não editável).

**Saída em FINANCEIRO.** `VINCULA?` com a mesma regra, mas sem mover protocolo
para a descrição nem usar `MIGRAÇÃO`. `VINCULA (POR NOME)?` recebe só SIM/NÃO,
comparando o nome do financeiro com uma lista única montada a partir dos nomes
de PROCESSOS (separados por `;`) e de CLIENTES, sem duplicatas e ordenada.

**Opções.** *Nome sem vínculo na descrição* (só FINANCEIRO): prefixa a descrição
com `NOME + " | " + DESCRIÇÃO` quando não há vínculo por nome. *Manter apenas um
campo vinculante* (AGENDA, FINANCEIRO ou ambos): mantém só o vínculo de maior
prioridade e concatena os demais ao fim da descrição, sem mover `MIGRAÇÃO`.

**Pendências.** Onde cada opção é ligada na UI, como concatenar quando o campo
de descrição está vazio e como tratar variações de grafia do mesmo nome.

## Manutenção

- Rodar `uv lock --upgrade` no início do ciclo e validar pandas/Flet — critério:
  testes verdes e app abrindo.
- Revisar `docs:check` no CI a cada mudança de documentação.
- Atualizar o code tour quando um módulo do core mudar de papel.

## Gatilhos (não são backlog)

- Suporte a macOS/Linux — só entra quando houver máquina para testar.
- Empacotamento, instalador e release — só entram quando o dono decidir
  distribuir.
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

## Notas do ciclo

- As duas adições do dono ao backlog viraram S6a (merge) e S6b (etapas); o tema
  claro segue como S6c.
- `LINHA_ORIGEM` usa a largura do total do resultado (12 linhas → `01`..`12`) e
  não reinicia por arquivo/aba.
- A barra indeterminada mostra atividade dentro de um arquivo; a fração só
  aparece quando o arquivo termina.
- O dono adicionou dois itens ao backlog: envio direto do Google Drive (login
  OAuth, múltiplas contas, link ou seletor) e vinculação entre AGENDA, CLIENTES,
  FINANCEIRO e PROCESSOS, com protocolo detalhado acima. Nenhum dos dois tem
  sessão marcada.
