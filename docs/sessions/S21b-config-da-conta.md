# S21b — Engrenagem da conta: foto e apelido

## Objetivo

A engrenagem no cabeçalho do painel de perfil abre a configuração da conta
selecionada: o usuário escolhe uma foto do disco e um apelido. A foto aparece
no avatar (sem foto, as iniciais) e o apelido substitui o nome no topo e no
painel.

## Fora de escopo

- Foto do perfil do Google (exigiria escopo `profile` ou chamada ao
  `userinfo`); só imagem local.
- Picker JS (S24), plugins e qualquer mudança no abrir/salvar do Drive.
- “Sobre o app” (backlog).

## Tarefas

1. Decidir por questionário: tela como diálogo (`AlertDialog`) ou página;
   formatos e tamanho máximo da foto; recorte circular automático ou não.
2. `shared/`: perfil por conta (apelido + foto) guardado em `drive/profiles/`
   com o mesmo hash de `AccountStore.path_for`; gravação atômica; foto copiada
   para dentro da pasta, nunca referenciada no lugar original.
3. `DriveSession.logout`: apagar apelido e foto junto com a conta (ADR 0029).
4. `ui/components/account_label.py`: `display_name` usa o apelido;
   `avatar` usa a foto em bytes (`CircleAvatar.foreground_image_src`), com as
   iniciais de fallback (`on_image_error`).
5. `ui/components/top_menu.py`: engrenagem (`ft.Icons.SETTINGS`) no canto
   superior direito do cabeçalho; tela de configuração com prévia, escolher
   foto, remover foto, apelido, salvar e cancelar.
6. Testes headless (perfil no store, logout apaga, apelido no topo, foto no
   avatar, cancelar não grava) e docs (`docs/reference/ui.md`, CHANGELOG).

## Aceite

- [ ] Engrenagem abre a configuração da conta selecionada.
- [ ] Apelido substitui o nome no topo e no painel; vazio volta ao nome.
- [ ] Foto aparece no avatar; sem foto, as iniciais.
- [ ] Sair apaga apelido e foto da conta, sem tocar nas outras.
- [ ] App conferido pelo dono nos dois temas (`uv run xl-utils --web` ajuda).
- [ ] `ruff`, `pytest` e `uv run python scripts/check_docs.py` verdes.

## Orçamento de contexto (≤90 linhas)

`docs/adr/0029-*.md` → **Decisão**; `ui/components/top_menu.py` (`_header`,
`_panel`); `ui/components/account_label.py` inteiro;
`shared/accounts.py` só `path_for`, `remove` e `_write_atomic`.

## Arquivos prováveis

- `src/xl_utils/ui/components/{top_menu,account_label}.py`
- `src/xl_utils/shared/accounts.py` (ou módulo novo de perfil)
- `src/xl_utils/ui/drive.py` (`logout`)
- `tests/test_top_menu.py`, `tests/test_accounts.py`

## Riscos

- Clique na engrenagem dentro do `SubmenuButton` pode não fechar o painel
  antes do diálogo: conferir cedo no `--web`.
- `FilePicker` no `--web` devolve bytes, não caminho: ler pelo que vier.
- Foto grande pesa no `CircleAvatar`: limitar tamanho na importação.
- O nome no topo tem até 16 caracteres (`TRIGGER_NAME_LIMIT`) para caber em
  `theme.TOP_MENU_RESERVE`; o apelido segue o mesmo limite.
- E-mail e apelido são dado pessoal: nada em log nem em diagnóstico.

## Próximo depois desta

S22 — Auditoria dos docs, documentação para quem chega e README.
