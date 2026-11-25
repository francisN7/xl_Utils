# ADR 0027 — Verificar Vínculos sai do app e vira plugin privado

- **Status:** aceita
- **Data:** 2026-11-25

## Contexto

A quinta ferramenta (ADRs 0014 e 0016) cruza AGENDA, FINANCEIRO, PROCESSOS e
CLIENTES com cabeçalhos e regras de um escritório só. O README já a tratava
como escopo pessoal: ela não serve a quem baixa o app público. Desde o ciclo
0008 existem plugins locais (ADR 0023), e ela era a única nativa com config
própria (`headers.json`, ADR 0015), exceções tipadas tratadas no `ToolLayout` e
um hook de pré-checagem (`pre_run`) com diálogo de reexecução.

## Decisão

- Remover a ferramenta do app na S19: core, controller, página,
  `shared/configs.py`, `configs/headers.json` e os testes.
- Tirar do `ToolLayout` o que só ela usava: as quatro exceções tipadas e o
  `pre_run` com o diálogo “Planilha já processada”. `inputs`, `ready` e `hint`
  ficam, porque a página declarativa dos plugins usa.
- Guardar o código no repo privado `xl_U-Plugins`, em `link/referencia/`
  (cópia de `4be82ef`), só como referência.
- Reescrever a vinculação como plugin depois da API 2 (S20), que dá ao plugin o
  leitor de planilhas do host.

## Consequências

- O app fica com quatro ferramentas nativas genéricas; o Início tem quatro
  cartões e Plugins continua no rodapé.
- A vinculação fica indisponível até o plugin existir.
- `configs/` guarda só o modelo do cliente OAuth; o padrão do ADR 0015 segue
  valendo para ele.
- O plugin vai precisar avisar a reexecução sem o `pre_run` do host.

## Alternativas

- **Manter nativa até o plugin ficar pronto:** sem lacuna, mas a API 2 mudaria
  o contrato com uma nativa ainda presa a hooks exclusivos.
- **Manter o `pre_run` no host para o plugin:** código morto e sem teste até lá;
  se a API 2 precisar, volta como parte do contrato.
- **Plugin no repo público:** expõe regras específicas do escritório.
