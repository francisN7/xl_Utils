# Índice dos ADRs

Uma linha por decisão. O arquivo completo guarda contexto, alternativas e
consequências; ele não muda depois de aceito (adendos entram no próprio ADR).

| # | Decisão | Status |
|---|---|---|
| [0001](0001-stack-ui-e-ambiente.md) | Stack, uv, Flet e fim do CLI | Aceita |
| [0002](0002-arquitetura-core-ui.md) | Arquitetura core/controllers/ui | Aceita |
| [0003](0003-ui-sidebar-e-inicio.md) | Sidebar com Início e anatomia de ferramenta | Aceita |
| [0004](0004-leitura-segura-e-emojis.md) | Leitura segura e limpeza compartilhada | Aceita |
| [0005](0005-selecao-de-abas-e-merge.md) | Seleção de abas e mesclagem com origem | Aceita |
| [0006](0006-lote-de-arquivos.md) | Lote de arquivos nas ferramentas | Aceita |
| [0007](0007-log-e-diagnostico.md) | Log estruturado e diagnóstico copiável | Aceita |
| [0008](0008-saida-escolhida.md) | Saída escolhida depois da prévia | Aceita |
| [0009](0009-publicacao-main-legacy.md) | UI na `main`, história antiga na `legacy` | Aceita |
| [0010](0010-leitura-fiel-csv-html.md) | Leitura fiel de CSV/HTML e `NA` como texto | Aceita |
| [0011](0011-execucao-fora-da-ui.md) | Execução fora da UI thread e progresso por arquivo | Aceita |
| [0012](0012-cnj-texto-sujo.md) | CNJ em texto sujo sem validar o dígito verificador | Aceita |
| [0013](0013-tema-claro-e-preferencia.md) | Tema claro opcional e preferência salva | Aceita |
| [0014](0014-regra-de-vinculacao.md) | Vinculação por valor bruto e `MIGRAÇÃO` | Aceita |
| [0015](0015-config-empacotada.md) | Config empacotada e estado por máquina | Aceita |
| [0016](0016-fluxos-e-opcoes-da-vinculacao.md) | Fluxos independentes e opções da vinculação | Aceita |
| [0017](0017-tela-cheia-do-quadro.md) | Tela cheia por overlay no conteúdo do merge | Aceita |
| [0018](0018-drive-autenticacao.md) | OAuth do Drive, contas e tokens | Aceita |
| [0019](0019-publicacao-do-site.md) | Publicação do site por workflow com filtro | Aceita |

## Como ler

- O ADR responde **por quê**; o código e `docs/reference/` respondem **o que é**.
- "Substituída" não apaga a decisão: mostra o que mudou e onde olhar agora.
- Decisão nova entra como `NNNN-titulo-curto.md` e ganha uma linha aqui.
