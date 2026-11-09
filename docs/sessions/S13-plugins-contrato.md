# S13 — Plugins I: contrato e extração segura

## Objetivo

Definir o contrato de plugins num ADR e entregar a instalação segura de um
pacote `.7z` em `%LOCALAPPDATA%/xl_utils/plugins/`, sem UI e sem carregar código.

## Fora de escopo

- Área “Plugins” na navegação, lista, instalar/remover pela tela e documentação
  pública — ficam na sessão seguinte.
- Plugins reais, marketplace, download automático ou assinatura de código.
- Mudar como as cinco ferramentas atuais são descobertas.
- UI de erro; nesta sessão a falha vira exceção/retorno testável.

## Tarefas

1. Escrever o ADR do contrato antes do código: manifesto (nome, id, versão,
   compatibilidade, entrypoint, permissões e dependências), API de UI mínima
   (sem importar o shell), ciclo de vida (descoberta, carregamento, falha
   isolada, desinstalação), o que o plugin pode e não pode fazer (rede,
   filesystem, subprocesso) e versionamento da API. Registrar a decisão entre
   mesmo processo e subprocesso com o risco de cada um.
2. Escolher e adicionar a biblioteca de `.7z` (avaliar `py7zr`), medindo o custo
   no instalador com `scripts/build_windows.ps1` antes de fixar.
3. Implementar a validação do pacote em módulo puro: recusar caminho absoluto,
   `..`, symlink, zip bomb e entradas que não sejam arquivo regular; conferir
   hash e tamanho; exigir manifesto válido e versão compatível.
4. Extrair para pasta temporária e só promover para
   `%LOCALAPPDATA%/xl_utils/plugins/<id>/` no fim, de forma atômica; rejeitar
   id repetido sem sobrescrever; desinstalar removendo a pasta do plugin.
5. Cobrir com testes: pacote válido, manifesto inválido, traversal, symlink,
   zip bomb, hash errado, versão incompatível, id duplicado e desinstalação.
   Nenhum teste executa código do pacote.
6. Atualizar `CHANGELOG.md`, `CURRENT.md` e a referência do contrato; escrever a
   spec da sessão seguinte.

## Aceite

- [ ] ADR do contrato aceito, com alternativa (processo × subprocesso) e riscos.
- [ ] Pacote válido instala e desinstala em `%LOCALAPPDATA%/xl_utils/plugins/`.
- [ ] Pacote malicioso (traversal, symlink, zip bomb) é recusado sem escrever
      fora da pasta e sem executar nada.
- [ ] Biblioteca `.7z` escolhida com medição do impacto no instalador.
- [ ] `ruff`, `pytest` e `node scripts/check-docs.mjs` verdes.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec e o ADR do contrato quando existir. Só
abrir `shared/` e os scripts de build ao editar; não reler o core das
ferramentas — a sessão não muda regra de negócio existente.

## Arquivos prováveis

- `docs/adr/0022-*.md`, `docs/adr/README.md`, `docs/reference/`
- `src/xl_utils/shared/` (ou `core/plugins/`), `pyproject.toml`, `uv.lock`
- `scripts/build_windows.ps1`, `installer/xl_utils.iss`
- `tests/`, `CHANGELOG.md`, `docs/state/CURRENT.md`

## Riscos

- `.7z` em Python é dependência nova e pesada: medir tamanho no instalador
  antes de espalhar pelo código; se pesar demais, considerar extração via 7-Zip
  externo só se o Windows tiver o binário.
- Zip bomb e symlink no Windows se comportam diferente do POSIX: testar com
  arquivos reais, não só com mock.
- Contrato sem ADR vira API acidental: nenhum código de plugin antes do ADR.
- O instalador embute o novo pacote: refazer o build e checar que a suíte e o
  app continuam abrindo.

## Próximo depois desta

Plugins II — área “Plugins” na UI, instalar/remover pela tela e o primeiro
exemplo público.
