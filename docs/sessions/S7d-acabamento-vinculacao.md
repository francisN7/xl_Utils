# S7d — Acabamento da vinculação

## Objetivo

Fechar o acabamento da ferramenta Verificar Vínculos: log por etapa, cartão no
Início e revisão dos textos, sem mudar a regra entregue na S7c.

## Fora de escopo

- Reabrir a regra de vinculação, as opções ou os fluxos.
- Google Drive e tela cheia.

## Tarefas

1. Conferir o log por etapa nos dois fluxos: leitura, planilha carregada,
   vinculação concluída e totais por CNJ/PASTA/PROTOCOLO/nome.
2. Ajustar o cartão do Início para refletir as quatro planilhas e os fluxos.
3. Revisar textos da página, das opções e das mensagens de erro/aviso.
4. Revisar a documentação viva e o code tour.
5. Rodar os exemplos reais de `xl_Utils_exemplos_vinculacao` (fora do repo):
   grupo 1 contra o gabarito; grupo 2 como referência visual.
6. Fechar com lint, testes, docs e commit.

## Aceite

- [x] Log mostra leitura e totais dos dois fluxos.
- [x] Início descreve a ferramenta com as quatro planilhas.
- [x] Textos sem “AGENDA e PROCESSOS” onde já são quatro.
- [x] Grupo 1 bate com o gabarito.
- [x] Lint, testes e docs verdes.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec e o ADR 0016. Consultar
`ui/pages/link.py`, `controllers/link.py`, `ui/pages/home.py` e
`docs/reference/ui.md`.

## Arquivos prováveis

- `src/xl_utils/controllers/link.py`, `ui/pages/link.py`,
  `ui/pages/registry.py`, `ui/pages/home.py`
- `tests/test_link.py`, `tests/test_link_page.py`
- `docs/reference/ui.md`, `CHANGELOG.md`

## Riscos

- O cartão do Início pode ficar longo com quatro planilhas; manter uma frase.
- Não reintroduzir `MIGRAÇÃO` como dado nem normalizar nomes.

## Próximo depois desta

S8 — tela cheia no merge.
