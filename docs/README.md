# Mapa da documentação

Este arquivo é o índice. A regra é **abrir a seção, não o arquivo inteiro**.

> **Orçamento por sessão:** `AGENTS.md` (≤100 linhas) + `docs/state/CURRENT.md`
> (≤60) + a spec da sessão (≤90). Tudo além disso é consulta pontual. Se a
> informação não está aqui, ela vive no Git (`git log`, `git show`) ou num ADR.

## Quem lê o quê

| Público | Documentos |
|---|---|
| 🤖 agente | `AGENTS.md`, `state/CURRENT.md`, `sessions/` (spec da vez) |
| 🤝 ambos | este mapa, `guide/`, `reference/`, `plugins/`, `roadmap/`, `adr/` |
| 👤 pessoas | `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`, o site (`index.html`) |

## Por pergunta

| Você quer… | Leia |
|---|---|
| chegar do zero à primeira contribuição | [`guide/onboarding.md`](guide/onboarding.md) |
| saber o que um termo quer dizer | [`reference/glossary.md`](reference/glossary.md) |
| contribuir (fluxo, regras e validação) | [`../CONTRIBUTING.md`](../CONTRIBUTING.md) |
| entender o projeto e ver as ferramentas | [`../README.md`](../README.md) |
| saber onde paramos | [`state/CURRENT.md`](state/CURRENT.md) |
| saber o que vem agora | [`roadmap/main.md`](roadmap/main.md) |
| entender o processo do roadmap | [`roadmap/README.md`](roadmap/README.md) |
| ver o que já foi entregue | [`roadmap/README.md`](roadmap/README.md) |
| entender as regras do agente | [`../AGENTS.md`](../AGENTS.md) |
| relatar uma falha de segurança | [`../SECURITY.md`](../SECURITY.md) |
| rodar o projeto | [`guide/setup.md`](guide/setup.md) |
| gerar e publicar o instalador | [`guide/release-windows.md`](guide/release-windows.md) |
| testar | [`guide/testing.md`](guide/testing.md) |
| entender como o código é organizado | [`reference/architecture.md`](reference/architecture.md) |
| ler o código em ordem guiada | [`guide/code-tour.md`](guide/code-tour.md) |
| entender a UI e o tema | [`reference/ui.md`](reference/ui.md) |
| criar um plugin | [`plugins/README.md`](plugins/README.md) |
| criar o primeiro plugin, passo a passo | [`plugins/primeiro-plugin.md`](plugins/primeiro-plugin.md) |
| empacotar e testar um plugin | [`plugins/empacotar-testar.md`](plugins/empacotar-testar.md) |
| ver o site público | [`index.html`](index.html) |
| trocar banner ou capturas (README e site) | [`assets/`](assets/) e [`guide/setup.md` → Site público](guide/setup.md#site-público) |
| ler a política de privacidade | [`privacy.html`](privacy.html) |
| saber **por que** algo é assim | [`adr/`](adr/) |
| ver o que mudou | [`../CHANGELOG.md`](../CHANGELOG.md) |
| ler a spec da próxima sessão | [`sessions/S23-release-0-4-0.md`](sessions/S23-release-0-4-0.md) |

## Por seção (atalho)

| Preciso de… | Vá direto a | ~linhas |
|---|---|---|
| camadas e fluxo de dados (diagramas) | `reference/architecture.md` → **Camadas** e **Fluxo de dados** | 60 |
| mapa dos módulos do core | `reference/architecture.md` → **Mapa do core** | 20 |
| papel de cada módulo fora do core | `reference/architecture.md` → **Mapa dos módulos** | 55 |
| ordem de leitura do código | `guide/code-tour.md` → **As paradas** | 90 |
| limites conhecidos da leitura | `reference/architecture.md` → **Limites conhecidos** | 10 |
| pipeline de leitura segura | `reference/architecture.md` → **Leitura segura** | 20 |
| detecção de formato e MIME | `reference/architecture.md` → **Detecção de formato** | 15 |
| saída e gravação | `reference/architecture.md` → **Saída** | 12 |
| layout, navegação e tema | `reference/ui.md` → **Layout** | 30 |
| contrato de plugins | `plugins/README.md` → **Mapa do contrato** | 20 |
| criar, empacotar e testar um plugin | `plugins/primeiro-plugin.md` → **Empacotar** | 40 |
| carregamento e ciclo de vida do plugin | `reference/architecture.md` → **Plugins** | 15 |
| comandos do dia a dia | `guide/setup.md` → **Rodando** | 15 |
| como escrever teste | `guide/testing.md` → **O que testar** | 20 |
| o que cada arquivo de teste prova | `guide/code-tour.md` → **11. Testes** | 50 |
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
| por que a vinculação comparava valor bruto (substituída) | `adr/0014-regra-de-vinculacao.md` | 45 |
| por que a config viaja no pacote | `adr/0015-config-empacotada.md` | 40 |
| por que os fluxos da vinculação vinham dos anexos (substituída) | `adr/0016-fluxos-e-opcoes-da-vinculacao.md` | 45 |
| por que a tela cheia é overlay no conteúdo | `adr/0017-tela-cheia-do-quadro.md` | 35 |
| por que o Drive usa OAuth, DPAPI e contas separadas | `adr/0018-drive-autenticacao.md` | 55 |
| por que o site só publica quando o HTML muda | `adr/0019-publicacao-do-site.md` | 45 |
| por que o histórico é uma página por ciclo | `adr/0020-arquivo-do-historico.md` | 35 |
| por que o instalador usa PyInstaller e Inno Setup | `adr/0021-instalador-windows.md` | 70 |
| por que os ciclos fechados ficam no roadmap | `adr/0022-ciclos-no-roadmap.md` | 35 |
| por que plugins usam `.tar.xz` e mesmo processo | `adr/0023-contrato-de-plugins.md` | 120 |
| por que o plugin só é importado ao executar | `adr/0024-carregamento-sob-demanda.md` | 45 |
| por que o seletor do Drive é Flet puro e paginado | `adr/0025-seletor-de-arquivos.md` | 115 |
| por que a vinculação saiu do app | `adr/0027-vinculacao-vira-plugin.md` | 45 |
| por que o plugin lê por `request.reader` e a API 1 saiu | `adr/0028-api-2-reader.md` | 70 |
| por que o Drive tem painel de perfil e conta selecionada | `adr/0029-painel-de-perfis-do-drive.md` | 68 |
| por que o token do Drive vai para o chaveiro fora do Windows | `adr/0030-token-no-chaveiro-fora-do-windows.md` | 53 |
| por que a foto e o apelido da conta ficam em `drive/profiles/` | `adr/0031-perfil-local-da-conta.md` | 60 |

## Regras do mapa

- **Guide** responde "como eu faço"; **reference**, "como X é".
- **ADR** guarda o **por quê** e não muda depois de aceito.
- **Spec de sessão** é escopo fechado e temporário: no encerramento, entrega e
  aceite viram linha em `roadmap/main.md` e a spec sai (`git rm`).
- **Histórico** é a página `NNNN-titulo.md` em `roadmap/`, uma por ciclo, ao
  lado do `main.md`. O passado fica em texto no Git; não existe arquivo
  comprimido no repositório.
- **CURRENT** é estado, não narrativa: sem medições, diffs ou tabelas antigas.
- Referência não conta em que sessão a coisa foi feita; isso é histórico.
- Documento novo só entra se responder uma pergunta que nenhum outro responde.

## O que é histórico

`CHANGELOG.md`, os ADRs e os ciclos fechados em `roadmap/NNNN-*.md` registram o
passado: nomes de documentos e sessões citados neles podem não existir mais. O
check de docs valida os documentos vivos, ignora o corpo do CHANGELOG, das specs
de sessão e dos ADRs, e confere os índices, inclusive `adr/README.md`. Ele
também exige que todo módulo de `src/xl_utils/` apareça em
`reference/architecture.md` ou `guide/code-tour.md`.
