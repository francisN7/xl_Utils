# Contribuindo

O xl_Utils é um projeto pessoal com código público para consulta. Não há
licença de uso (ver [README → Licença](README.md#licença)), então este guia é
para quem foi **convidado** a contribuir. Quer sugerir algo sem convite? Abra
uma issue ou fale com o dono pelo perfil do GitHub **antes** de mandar um pull
request.

Primeira vez aqui? Comece pela [trilha de onboarding](docs/guide/onboarding.md).

## Fluxo de uma mudança

1. **Escopo.** O trabalho anda em sessões (`SNN`): cada uma tem uma spec em
   `docs/sessions/` e uma linha em
   [`docs/roadmap/main.md`](docs/roadmap/main.md). Mudança fora de uma spec
   começa com uma conversa com o dono.
2. **Onde mexer.** Use a tabela
   [**Onde mexer para…**](docs/guide/code-tour.md#onde-mexer-para) do code tour.
   A regra fica em `core/` (puro, sem Flet), o controller orquestra e a página
   só coleta e exibe.
3. **Teste.** Toda regra nova ganha teste com dados fictícios
   ([`testing.md`](docs/guide/testing.md)). A UI tem testes headless.
4. **Docs.** Atualize o que a mudança torna falso. Módulo novo precisa
   aparecer em `docs/reference/architecture.md` → **Mapa dos módulos** ou no
   code tour; o check de docs cobra.
5. **Validação.** Os quatro comandos abaixo precisam ficar verdes.
6. **Commit.** Pequeno, com mensagem `SNN: resumo curto` em PT-BR. O push fica
   com o dono.

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
uv run python scripts/check_docs.py
```

## Convenções

- Identificadores em inglês; comentários, docstrings, UI e docs em PT-BR.
- Toda ferramenta lê pelo pipeline `all_str` (`prepare_workbook`); quebras de
  linha e zeros à esquerda são preservados.
- O arquivo do usuário nunca é renomeado nem alterado.
- Dependência nova só com `uv add`; `uv.lock`, `output/` e `dist/` não se editam
  à mão.
- Decisão de arquitetura relevante vira ADR em
  [`docs/adr/`](docs/adr/README.md).

## Dados e segredos

- Planilhas de teste, prints e exemplos usam **dados fictícios**: nada de CPF,
  CNPJ, nome de cliente ou planilha real.
- Nunca commite `.env`, JSON de cliente OAuth, token, chave ou backup. Estado e
  segredos ficam em `%LOCALAPPDATA%/xl_utils/` (Linux: `~/.xl_utils/` e o
  chaveiro).
- Falha de segurança não vai para issue pública: siga o
  [`SECURITY.md`](SECURITY.md).

## Plugins

Ferramenta de fluxo específico entra como plugin, fora do app. O caminho está
em [`docs/plugins/primeiro-plugin.md`](docs/plugins/primeiro-plugin.md).
