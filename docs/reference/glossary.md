# Glossário

**O que responde:** o que cada termo do domínio, do código e do processo quer
dizer neste projeto. **O que não responde:** como as peças se ligam (ver
[`architecture.md`](architecture.md)) nem por que são assim (ver
[`../adr/`](../adr/README.md)).

## Planilhas e ferramentas

| Termo | Significado |
|---|---|
| **CNJ** | Numeração única de processo judicial: 20 dígitos no formato `NNNNNNN-DD.AAAA.J.TR.OOOO`. A extração aceita separadores sujos e não valida o dígito verificador (ADR 0012); a saída é a coluna `PROCESSOS`. |
| **`all_str`** | O pipeline de leitura por onde toda ferramenta passa: lê tudo como texto, remove emojis, preserva zeros, quebras de linha e `NA`. A porta de entrada é `prepare_workbook`. Também é a ferramenta **Tratamento de Texto**. |
| **aba** | Uma planilha dentro do arquivo (sheet). CSV vira `Planilha1`; cada tabela de HTML vira `PáginaN`. |
| **seleção de abas** | Os chips que escolhem quais abas entram. No lote, todas vêm marcadas; no merge, só a primeira de cada arquivo (ADR 0006). |
| **lote** | Vários arquivos numa execução. Texto, CNJ e recorte tratam cada um à parte; o merge junta todos. |
| **formato real** | O tipo detectado pelo conteúdo (`core/mime.py`), que vence a extensão. O arquivo do usuário nunca é renomeado. |
| **`SaveItem`** | Um livro pronto em memória, com nome sugerido e pasta `output/` da origem. Nada é gravado até o usuário escolher. |
| **Pronto para salvar** | Estado do painel depois de executar: a prévia aparece, os botões de salvar liberam, o disco continua intacto. |
| **`output/`** | Pasta ao lado do arquivo de origem usada pelo atalho **Salvar em output/**. Fica fora do Git. |
| **`_parteN`** | Sufixo dos arquivos quando uma aba passa de `ROW_LIMIT` (1.000.000) linhas: `nome_parte1.xlsx`, `nome_parte2.xlsx`… |
| **`ORIGEM` / `LINHA_ORIGEM`** | Primeiras colunas do merge: `<arquivo sem extensão> - <aba>` e a posição da linha no resultado, com zeros à esquerda. |
| **slot nomeado** | Uma entrada de arquivo com papel fixo num plugin (`[[ui.inputs]]`), como AGENDA ou FINANCEIRO. São exemplos de rótulo, não regras do app. |

## Interface

| Termo | Significado |
|---|---|
| **Início** | O hub com um cartão por ferramenta nativa. |
| **`ToolLayout`** | A anatomia comum de toda ferramenta: entrada, opções, resultado e barra de ação; roda o trabalho fora da UI thread. |
| **`ToolState`** | O estado de uma ferramenta (arquivos, abas, opções, resultado), preservado quando o usuário navega. |
| **log e diagnóstico** | `RunLog` registra as etapas; “Copiar diagnóstico” junta versões, arquivos, opções e erro, nunca conteúdo de célula. |
| **Dracula / Alucard** | Os temas escuro e claro. Alucard é a variante clara do Dracula; a escolha fica em `settings.json`. |

## Google Drive

| Termo | Significado |
|---|---|
| **`drive.file`** | O único escopo de arquivos pedido: o app só enxerga o que criou ou o que o usuário escolheu no Picker. |
| **Picker** | O seletor do Google que abre no navegador para escolher arquivo ou pasta. Hoje é o de apps desktop; o Picker JS está no backlog (ADR 0026). |
| **conta selecionada** | A conta mostrada no topo; “Abrir do Drive” usa essa (ADR 0029). |
| **conta de origem** | A conta que abriu o arquivo; “Salvar no Drive” grava sempre nela, mesmo com outra selecionada. |
| **concessão de pasta** | A pasta do Drive que o usuário autorizou uma vez para receber gravações, guardada por conta em `folders.json`. |
| **cache do Drive** | A cópia local do arquivo aberto do Drive, com o nome real; entra no pipeline como qualquer arquivo. |
| **cofre** | Onde o `refresh_token` fica: DPAPI no Windows, chaveiro do sistema no Linux (ADR 0030). |
| **perfil local** | Apelido e foto escolhidos para cada conta, em `drive/profiles/`; não sincroniza com o Google (ADR 0031). |

## Plugins

| Termo | Significado |
|---|---|
| **plugin** | Pacote local que acrescenta uma ferramenta. Roda no mesmo processo, sem sandbox. |
| **manifesto** | O `plugin.toml`: identidade, permissões, página e opções. Lido sem executar código. |
| **pacote e sidecar** | O `.tar.xz` do plugin e o arquivo `.sha256` ao lado, que prova integridade (não autoria). |
| **`api_version`** | A versão do contrato com o host. Hoje só a `2`, que traz o `request.reader`. |
| **`request.reader`** | A leitura de planilhas que o host entrega ao plugin, pelo mesmo pipeline `all_str`. |
| **`data/`** | Pasta persistente do plugin; some na desinstalação. |

## Processo de trabalho

| Termo | Significado |
|---|---|
| **sessão `SNN`** | Uma entrega vertical com testes, docs e commit. Sessão inserida no meio ganha letra (`S22a`, `S22b`). |
| **spec** | O escopo fechado de uma sessão em `docs/sessions/`; sai do repositório quando a sessão fecha. |
| **ciclo** | Um grupo de sessões com o mesmo tema. Fechado, vira `docs/roadmap/NNNN-titulo.md`. |
| **`CURRENT.md`** | O estado entre sessões: o que foi feito, o que vem e as armadilhas. |
| **ADR** | Registro de decisão: guarda o porquê e não é reescrito depois de aceito. |
| **selo** | A última linha de uma entrega: “Sessão fechada”, “Sessão aberta” ou “Sem sessão”. |
