# S24 — Seletor de arquivos do Drive (implementação)

> **Backlog:** spec reescopada após o adendo do ADR 0025. Depende da S16
> (ADR 0026) e entra depois da 0.4.0 se o dono priorizar. **Arquivo local
> continua no seletor nativo do sistema operacional.**

## Objetivo

Substituir o Picker do Google que abre o navegador por um seletor de pastas e
arquivos do Drive dentro do app, no tema, com paginação, busca, filtro por
formato e pastas recentes, usando o pipeline de token decidido na S16. O
download continua no cache local e entrega o caminho ao `FileInput`.

## Fora de escopo

- Seletor de arquivos locais; o nativo do sistema operacional é o padrão e não
  muda.
- Decidir escopo OAuth, verificação do Google ou o pipeline da S16; esta spec
  consome o ADR 0026.
- Migrar a stack, embutir webview ou mexer no menu de perfis (S21).
- Arrastar e soltar do sistema operacional.

## Tarefas

1. Implementar o cliente/controlador de listagem do Drive conforme o ADR 0026:
   pastas, arquivos, `nextPageToken`, filtro por MIME/extensão, busca e
   tratamento de token expirado/sem permissão.
2. `ui/components/drive_selector.py`: diálogo/overlay com breadcrumb, subir,
   busca, filtro, lista paginada e seleção; tamanho relativo à janela, testado
   em 100%, 125% e 150%.
3. Recentes: guardar apenas pastas/arquivos do Drive (id, nome, conta) em
   `%LOCALAPPDATA%/xl_utils`, sem token e sem caminho do cache.
4. Integrar ao botão do Drive no `FileInput`; o seletor nativo local e o Picker
   continuam como fallback. O download e a gravação continuam em
   `drive_cache`/`DriveSession`.
5. Testes com API falsa: paginação, pasta vazia, token expirado, arquivo que não
   é planilha, multi-conta e cache; um teste manual com a conta de teste.
6. Atualizar `docs/reference/ui.md`, `architecture.md`, code tour e CHANGELOG.

## Aceite

- [ ] O botão do Drive abre o seletor no tema, sem sair para o navegador.
- [ ] Pastas, arquivos, busca, filtro e paginação funcionam com a API falsa.
- [ ] O arquivo escolhido vira o mesmo caminho de cache que o Picker entrega.
- [ ] Seletor nativo local e Picker continuam disponíveis como fallback.
- [ ] Erros de token/permissão têm mensagem clara, sem traceback.
- [ ] `ruff`, `pytest` e `node scripts/check-docs.mjs` verdes.

## Orçamento de contexto (≤90 linhas)

Ler o ADR 0025 (com o adendo), o ADR 0026, `shared/drive.py`,
`drive_auth.py`, `drive_pick.py`, `drive_store.py`, `ui/drive.py`,
`ui/components/file_input.py`, `docs/reference/ui.md` → **Entrada de arquivos**
e `architecture.md` → **Drive**.

## Arquivos prováveis

- `src/xl_utils/shared/drive_list.py` (ou equivalente), `tests/test_drive_list.py`
- `src/xl_utils/ui/components/drive_selector.py`, `tests/test_drive_selector.py`
- `src/xl_utils/ui/components/file_input.py`, `tests/test_file_input_drive.py`
- `docs/reference/ui.md`, `docs/reference/architecture.md`,
  `docs/guide/code-tour.md`, `CHANGELOG.md`

## Riscos

- Listagem do Drive é API, não disco: latência e cota dominam; paginar e tratar
  `nextPageToken`, `403` e `404`.
- Escopo restrito e verificação do Google são decisão da S16; não prometer
  publicação sem o ADR 0026.
- Token expirado no meio da navegação precisa de mensagem e novo login sem
  perder a pasta atual.
- Conta errada, pasta compartilhada e “Meu Drive” versus “Compartilhados”
  precisam de estado explícito.
- Flet não virtualiza a lista no processo Python: nunca montar milhares de
  linhas; paginar e listar fora da UI thread.
- O cache do Drive é limpo no início do app; recentes não podem apontar para
  caminho temporário.

## Próximo depois desta

Se o seletor do Drive estabilizar, avaliar remover o Picker do botão do Drive e
manter o nativo local como está; o fallback do Picker fica no menu.
