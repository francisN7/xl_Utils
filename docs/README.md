# Mapa da documentação

Este arquivo é o índice. A regra é **abrir a seção, não o arquivo inteiro**.

> **Orçamento por sessão:** `AGENTS.md` (≤100 linhas) + `docs/state/CURRENT.md`
> (≤60) + a spec da sessão (≤90). Tudo além disso é consulta pontual. Se a
> informação não está aqui, ela vive no Git (`git log`, `git show`) ou num ADR.

## Por pergunta

| Você quer… | Leia |
|---|---|
| entender o projeto e ver as ferramentas | [`../README.md`](../README.md) |
| saber onde paramos | [`state/CURRENT.md`](state/CURRENT.md) |
| saber o que vem agora | [`roadmap/main.md`](roadmap/main.md) |
| ver o que já foi entregue | [`roadmap/README.md`](roadmap/README.md) |
| entender as regras do agente | [`../AGENTS.md`](../AGENTS.md) |
| relatar uma falha de segurança | [`../SECURITY.md`](../SECURITY.md) |
| rodar o projeto | [`guide/setup.md`](guide/setup.md) |
| testar | [`guide/testing.md`](guide/testing.md) |
| entender como o código é organizado | [`reference/architecture.md`](reference/architecture.md) |
| ler o código em ordem guiada | [`guide/code-tour.md`](guide/code-tour.md) |
| entender a UI e o tema | [`reference/ui.md`](reference/ui.md) |
| saber **por que** algo é assim | [`adr/`](adr/) |
| ver o que mudou | [`../CHANGELOG.md`](../CHANGELOG.md) |
| ler a spec da próxima sessão | [`sessions/S9a-drive-autenticacao.md`](sessions/S9a-drive-autenticacao.md) |

## Por seção (atalho)

| Preciso de… | Vá direto a | ~linhas |
|---|---|---|
| camadas e fluxo de dados | `reference/architecture.md` → **Camadas** | 30 |
| mapa dos módulos do core | `reference/architecture.md` → **Mapa do core** | 20 |
| ordem de leitura do código | `guide/code-tour.md` → **As paradas** | 90 |
| limites conhecidos da leitura | `reference/architecture.md` → **Limites conhecidos** | 10 |
| pipeline de leitura segura | `reference/architecture.md` → **Leitura segura** | 20 |
| detecção de formato e MIME | `reference/architecture.md` → **Detecção de formato** | 15 |
| saída e gravação | `reference/architecture.md` → **Saída** | 12 |
| layout, navegação e tema | `reference/ui.md` → **Layout** | 30 |
| comandos do dia a dia | `guide/setup.md` → **Rodando** | 15 |
| como escrever teste | `guide/testing.md` → **Testes** | 20 |
| por que Flet, uv e Python 3.15 | `adr/0001-stack-ui-e-ambiente.md` | 35 |
| por que core/controllers/ui | `adr/0002-arquitetura-core-ui.md` | 35 |
| por que sidebar + Início | `adr/0003-ui-sidebar-e-inicio.md` | 30 |
| por que leitura sempre em texto | `adr/0004-leitura-segura-e-emojis.md` | 30 |
| por que seleção de abas e merge por origem | `adr/0005-selecao-de-abas-e-merge.md` | 35 |
| por que lote de arquivos e seleção padrão | `adr/0006-lote-de-arquivos.md` | 35 |
| por que log estruturado e diagnóstico | `adr/0007-log-e-diagnostico.md` | 35 |
| por que salvar só depois da escolha | `adr/0008-saida-escolhida.md` | 35 |
| por que `main` tem UI e `legacy` só história | `adr/0009-publicacao-main-legacy.md` | 35 |
| por que CSV/HTML são lidos com separador e `NA` | `adr/0010-leitura-fiel-csv-html.md` | 30 |
| por que a execução sai da UI thread | `adr/0011-execucao-fora-da-ui.md` | 35 |
| por que CNJ sujo é extraído sem validar o dígito | `adr/0012-cnj-texto-sujo.md` | 35 |
| por que existe tema claro e preferência salva | `adr/0013-tema-claro-e-preferencia.md` | 40 |
| por que a vinculação compara valor bruto | `adr/0014-regra-de-vinculacao.md` | 45 |
| por que a config viaja no pacote | `adr/0015-config-empacotada.md` | 40 |
| por que os fluxos da vinculação vêm dos anexos | `adr/0016-fluxos-e-opcoes-da-vinculacao.md` | 45 |
| por que a tela cheia é overlay no conteúdo | `adr/0017-tela-cheia-do-quadro.md` | 35 |

## Regras do mapa

- **Guide** responde "como eu faço"; **reference**, "como X é".
- **ADR** guarda o **por quê** e não muda depois de aceito.
- **Spec de sessão** é escopo fechado e temporário; as specs do ciclo ativo
  saem quando o ciclo fecha.
- **CURRENT** é estado, não narrativa: sem medições, diffs ou tabelas antigas.
- Referência não conta em que sessão a coisa foi feita; isso é histórico.
- Documento novo só entra se responder uma pergunta que nenhum outro responde.

## O que é histórico

`CHANGELOG.md`, os ADRs e os ciclos fechados em `roadmap/NNNN-*.md` registram o
passado: nomes de documentos e sessões citados neles podem não existir mais. O
check de docs valida os documentos vivos, ignora o corpo do CHANGELOG, das specs
de sessão e dos ADRs, e confere os índices, inclusive `adr/README.md`.
