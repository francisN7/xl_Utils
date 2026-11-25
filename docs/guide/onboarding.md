# Onboarding — do zero à primeira contribuição

**O que responde:** em que ordem ler e o que fazer para entender, rodar e mexer
no xl_Utils pela primeira vez. **O que não responde:** os detalhes de cada
etapa; cada passo aponta para o documento que já os tem.

Reserve cerca de uma hora. Cada etapa termina com um “pronto quando…” para
você saber que pode seguir.

## 1. O que é

Leia o [`README.md`](../../README.md) até **Ferramentas**: quatro utilitários
de planilha (texto, CNJ, recorte e mesclagem) num app desktop em Flet, com
plugins locais e Google Drive opcional.

**Pronto quando** você souber dizer o que cada ferramenta faz e que toda
leitura passa pelo pipeline `all_str`.

## 2. Rodar

Siga [`setup.md`](setup.md) → **Rodando** e **Verificações**: `uv sync`,
`uv run xl-utils` e os quatro comandos de validação. Sem Windows, tudo roda no
Linux; `--web` abre a mesma interface no navegador.

**Pronto quando** o app abrir, você executar uma ferramenta com a planilha de
`uv run python scripts/make_fixture.py` e `uv run pytest` ficar verde.

## 3. Arquitetura

Leia [`architecture.md`](../reference/architecture.md) → **Camadas** e
**Fluxo de dados**. Os dois diagramas mostram as quatro camadas (`core`,
`controllers`, `ui`, `shared`) e o caminho de um arquivo até a gravação.

**Pronto quando** você souber por que `core/` não importa Flet e por que nada é
gravado antes da escolha do usuário.

## 4. Tour do código

Percorra o [`code-tour.md`](code-tour.md) → **As paradas**, na ordem. Abra cada
arquivo citado ao lado. O **Mapa dos módulos** de `architecture.md` diz o papel
de cada arquivo que o tour não visita.

**Pronto quando** você conseguir seguir um clique em **Executar** desde a
página até o `SaveItem`.

## 5. Vocabulário

Deixe o [`glossary.md`](../reference/glossary.md) aberto. Termos como conta
selecionada, `_parteN` e slot nomeado têm sentido próprio aqui.

**Pronto quando** os nomes das tabelas do code tour não forem mais estranhos.

## 6. Primeira contribuição

Leia o [`CONTRIBUTING.md`](../../CONTRIBUTING.md): o fluxo por sessão, as
regras de dados fictícios e a tabela **Onde mexer para…** do code tour. Uma boa
primeira tarefa é pequena e tem teste: um caso de borda numa regra de
`core/tools/` ou um ajuste de texto na UI.

**Pronto quando** sua mudança passar nos quatro comandos de validação e virar
um commit local com mensagem `SNN: resumo`.

## Depois

- Por que algo é assim: [`docs/adr/`](../adr/README.md).
- Criar um plugin em vez de mexer no app:
  [`plugins/primeiro-plugin.md`](../plugins/primeiro-plugin.md).
- Mapa completo da documentação: [`docs/README.md`](../README.md).
