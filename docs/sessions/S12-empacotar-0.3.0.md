# S12 — Empacotar a primeira versão, 0.3.0

## Objetivo

Gerar o instalador do Windows da 0.3.0, com Python e dependências embutidos,
instalável pelo usuário comum, com entrada no menu Iniciar, atalho opcional na
área de trabalho, ícone próprio, desinstalação limpa e artefato publicado nas
Releases do GitHub.

## Fora de escopo

- Plugins, seletor próprio de arquivos e mudança de escopo do Drive.
- macOS, Linux, assinatura de código paga ou Microsoft Store.
- Auto-update dentro do app.

## Tarefas

1. Medir as opções antes de decidir: PyInstaller + Inno Setup, Nuitka +
   Inno Setup e NSIS/MSIX. Comparar tamanho do artefato, tempo de build,
   compatibilidade com Flet 1.1.2 e esforço do script de instalação. Registrar
   a escolha em ADR novo (`docs/adr/`) com a alternativa descartada.
2. Montar o build a partir do wheel (`uv build`): coletar o pacote, `configs/`,
   o cliente OAuth empacotado (vazio por padrão) e os assets/ícone. Nada de
   `.venv`, `output/`, cache do Drive, contas ou dados reais no pacote.
3. Escrever o script do instalador: instalação por usuário (sem admin, se
   possível), menu Iniciar, atalho opcional na área de trabalho, ícone do app,
   versão 0.3.0 nos metadados e desinstalação que remove arquivos e atalhos sem
   tocar em `%LOCALAPPDATA%/xl_utils/` (contas e preferências).
4. Marcar **0.3.0** em `pyproject.toml`, `uv.lock` (depois de `uv lock`),
   `src/xl_utils/__init__.py`, diagnóstico e docs; conferir que o instalador e o
   executável reportam a mesma versão.
5. Validar numa máquina sem Python de desenvolvimento: instalar, abrir pelo menu
   Iniciar, executar uma ferramenta com planilha fictícia, abrir o menu de
   perfis, desinstalar e conferir que atalhos e arquivos saíram. Registrar o
   roteiro em `docs/guide/`.
6. Publicar o instalador e as notas da 0.3.0 na página de Releases do GitHub
   (tag `v0.3.0`), com requisitos, tamanho e checksum; atualizar `CHANGELOG.md`,
   `docs/state/CURRENT.md` e a spec da próxima sessão.

## Aceite

- [ ] Instalador `.exe` instala e abre a 0.3.0 sem Python nem `uv` na máquina.
- [ ] Menu Iniciar, atalho opcional e ícone funcionam; desinstalação é limpa.
- [ ] Contas, tokens e preferências sobrevivem à desinstalação.
- [ ] Release `v0.3.0` publicada com artefato, checksum e notas.
- [ ] ADR do empacotador registrado e `ruff`, `pytest` e
      `node scripts/check-docs.mjs` verdes.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec e o ADR do empacotador quando existir.
Só abrir `pyproject.toml`, `src/xl_utils/app.py` e os scripts de build ao
editar. Não reler o core nem os controllers: a sessão não muda regra de negócio.

## Arquivos prováveis

- `pyproject.toml`, `uv.lock`, `src/xl_utils/__init__.py`
- `src/xl_utils/app.py`, `src/xl_utils/configs/`, assets/ícone
- `scripts/` (build e instalador), `.github/workflows/` (release)
- `docs/adr/`, `docs/guide/`, `CHANGELOG.md`, `docs/state/CURRENT.md`

## Riscos

- PyInstaller/Nuitka com Flet: validar cedo um build mínimo que abra a janela;
  se falhar, trocar de ferramenta antes de escrever o instalador.
- Antivírus e SmartScreen sem assinatura: documentar o aviso e oferecer o
  checksum; não comprar certificado nesta sessão.
- Build grande demais ou lento: medir e registrar; cortar dependências opcionais
  só se não quebrarem teste.
- `uv lock` pode subir dependências: conferir o diff e rodar a suíte.

## Próximo depois desta

Sistema de plugins, começando pelo ADR do contrato e pela extração segura do
`.7z`.
