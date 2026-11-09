# Histórico

Arquivo dos ciclos fechados. É texto, versionado e pesquisável: o passado não
sai do repositório, só sai do caminho do dia a dia.

## Como funciona

- **Fronteira é o ciclo**, não a sessão. Cada ciclo fechado vira uma página
  `NNNN-titulo.md` aqui; o `main.md` do [`roadmap`](../roadmap/main.md) começa
  vazio no ciclo seguinte.
- **Sessão não tem arquivo próprio.** A spec é escopo temporário: vive enquanto
  a sessão está aberta e sai do working tree no fim. O resumo do que foi feito
  fica na página do ciclo.
- **O Git é o arquivo.** O que sai do working tree continua em `git log`,
  `git show` e `git log -- docs/sessions`. Não há `.7z`, `.zip` ou cópia
  comprimida no repositório: binário não tem diff, não tem busca e o check de
  docs não alcança o conteúdo.
- **O que não é histórico fica fora daqui:** regras do agente (`AGENTS.md`),
  estado (`state/CURRENT.md`), guias, referência, ADRs e o backlog vivo.
- **Links para specs** em página de ciclo apontam para “histórico no Git”, sem
  caminho: o arquivo não existe mais no working tree.

## Ciclos fechados

| Arquivo | Ciclo | Fechado em | Resumo |
|---|---|---|---|
| [`0001-fundacao.md`](0001-fundacao.md) | Fundação | 2026-11-04 | app Flet, leitura segura, quatro ferramentas |
| [`0002-migracao.md`](0002-migracao.md) | Migração e publicação | 2026-11-04 | core/controllers/ui, `main` × `legacy` |
| [`0003-qualidade.md`](0003-qualidade.md) | Qualidade e clareza | 2026-11-04 | testes, log, diagnóstico, docs |
| [`0004-execucao-e-robustez.md`](0004-execucao-e-robustez.md) | Execução e robustez | 2026-11-04 | execução fora da UI, cancelamento, CNJ sujo |
| [`0005-polimento.md`](0005-polimento.md) | Polimento | 2026-11-06 | `ORIGEM`/`LINHA_ORIGEM`, tema claro |
| [`0006-backlog.md`](0006-backlog.md) | Backlog | 2026-11-08 | vinculação, tela cheia, Google Drive |
| [`0007-versoes-e-distribuicao.md`](0007-versoes-e-distribuicao.md) | Versão e distribuição | 2026-11-09 | 0.2.0, instalador 0.3.0 e release |

## Convenção de nomes

- `NNNN-titulo.md`, quatro dígitos, ordem cronológica de fechamento.
- O título é curto e descreve o tema do ciclo, não a sessão.
- A página do ciclo não muda depois de fechada, salvo correção de link.
