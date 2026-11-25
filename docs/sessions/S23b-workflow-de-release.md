# S23b — Workflow de release no GitHub Actions

## Objetivo

Gerar o instalador Windows e o AppImage Linux no GitHub Actions, só quando o
dono pedir, com smoke test e artefatos prontos para baixar.

## Fora de escopo

- Publicar a release, mudar a versão ou o CHANGELOG (S23c).
- Assinatura de código e validação humana no Windows.
- Mudanças no `ci.yml` e no `pages.yml`.

## Tarefas

1. `.github/workflows/release.yml` com **um gatilho só**:
   `workflow_dispatch`, com o input obrigatório `confirmar` (texto `build`).
   Sem `push`, `tag`, `paths`, `schedule`, `workflow_run` ou `release`.
2. Job `guarda` que falha se `confirmar != build`; os builds dependem dele.
3. Job `windows` (`windows-2025` ou fixo equivalente): Python 3.15 via `uv`,
   Inno Setup, `scripts/build_windows.ps1`; smoke test que instala em silêncio
   (`/VERYSILENT /CURRENTUSER`), abre o executável e confere que o processo
   fica vivo por alguns segundos sem erro no log.
4. Job `linux` (`ubuntu-24.04`): `scripts/build_linux.sh` (S23a); smoke test
   com `xvfb-run` abrindo o AppImage pelo mesmo critério.
5. Cada job sobe artefato (instalador ou AppImage + `SHA256SUMS.txt`) com
   `retention-days` curto. Nada de `gh release` nem de `contents: write`.
6. `permissions: contents: read`; `concurrency: release` sem cancelar; actions
   fixadas por SHA completo (política do repo); runners com versão fixa.
7. Adendo na ADR 0021 (build sai da máquina do dono para o CI) e seção “Build no
   CI” nos guias de release Windows e Linux.

## Aceite

- [ ] O workflow não aparece em nenhum push, tag ou PR (conferido no histórico
      de runs depois de pelo menos um push comum).
- [ ] Disparo com `confirmar` errado falha na guarda, sem build.
- [ ] Disparo certo gera os dois artefatos com SHA-256 e smoke test verde.
- [ ] Todo push e todo disparo feitos com o OK do dono.
- [ ] `ruff`, `pytest` e `uv run python scripts/check_docs.py` verdes.

## Orçamento de contexto (≤90 linhas)

`.github/workflows/{ci,pages}.yml` (padrão de SHA e permissões),
`scripts/build_windows.ps1`, `scripts/build_linux.sh`, `installer/xl_utils.iss`
(topo), `docs/adr/0021-instalador-windows.md`.

## Arquivos prováveis

- `.github/workflows/release.yml`
- `docs/adr/0021-instalador-windows.md`, `docs/guide/release-{windows,linux}.md`

## Riscos

- O build Windows nunca rodou fora da máquina do dono: Inno Setup no runner,
  `_lzma.pyd`, `python3t.dll` e caminhos do PowerShell.
- Cada ajuste precisa de push e disparo; agrupar as correções para gastar
  poucas rodadas.
- O runner não tem GPU nem sessão gráfica: o smoke test do Flet pode precisar
  de `xvfb` (Linux) ou falhar sem tela (Windows). Plano B: smoke test só com
  `--help`/import do bundle, registrado nas notas.

## Próximo depois desta

S23c — release 0.4.0 para Windows e Linux e fechamento do ciclo 0009.
