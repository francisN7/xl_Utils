# S21 — Menu de perfis do Drive sem troca de conta

## Objetivo

O menu do topo lista os perfis do Google Drive como submenus nativos, sem
`checked` nem conta ativa; "Sair desta conta" fica no submenu de cada e-mail,
e salvar no Drive continua usando a conta de origem do arquivo.

## Fora de escopo

- Picker JS (S24) e qualquer mudança no fluxo de abrir/salvar além da conta.
- Plugins, API 2 e `xl_U-Plugins`.
- Embutir cliente OAuth ou API key no build (backlog).

## Tarefas

1. Decidir por questionário: com várias contas e sem ativa, qual conta o
   "Abrir do Drive" usa (pergunta no botão, submenu do e-mail ou outra);
   o que acontece com `set_active`/`switch`/`next_account`; registrar em
   adendo do ADR 0026 ou ADR novo.
2. `ui/components/top_menu.py`: um submenu por e-mail (abrir, sair), sem
   `checked`; "Adicionar conta" continua no fim.
3. `ui/drive.py` e `shared/accounts.py`: tirar a troca de conta que não for
   mais usada; manter `account_for` (conta de origem no salvar).
4. Testes headless do menu e da sessão (`tests/test_drive_session.py` e
   teste novo do menu se faltar).
5. Docs afetados (`docs/guide/` do Drive, se citar a troca) e `CHANGELOG.md`.

## Aceite

- [ ] Menu sem `checked`; cada e-mail abre submenu com "Sair desta conta".
- [ ] Salvar no Drive usa a conta de origem do arquivo, com teste.
- [ ] Sair de uma conta não afeta as outras nem os arquivos já abertos.
- [ ] App conferido pelo dono nos dois temas (`uv run xl-utils --web` ajuda).
- [ ] `ruff`, `pytest` e `uv run python scripts/check_docs.py` verdes.

## Orçamento de contexto (≤90 linhas)

`ui/components/top_menu.py` (só `_items` e handlers); `ui/drive.py` só
`switch`, `next_account`, `logout`, `account_for`, `open_from_drive`;
`shared/accounts.py` só `set_active`; `docs/adr/0026-*.md` → **Decisão**.

## Arquivos prováveis

- `src/xl_utils/ui/components/top_menu.py`, `src/xl_utils/ui/drive.py`
- `src/xl_utils/shared/accounts.py`, `src/xl_utils/ui/components/file_input.py`
- `tests/test_drive_session.py`, `tests/test_accounts.py`,
  `tests/test_file_input_drive.py`

## Riscos

- `PopupMenuItem` aninhado no Flet 1.x pode não abrir no web/desktop igual:
  conferir cedo no `--web` e no app.
- Tirar a conta ativa pode deixar o "Abrir do Drive" sem conta definida.
- `drive.file` só vê o que o app criou ou o Picker concedeu.

## Próximo depois desta

S22 — Auditoria dos docs, documentação para quem chega e README.
