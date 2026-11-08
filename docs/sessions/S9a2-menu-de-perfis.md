# S9a2 — Menu de perfis no canto superior direito

## Objetivo

Ajustar o login do Drive ao uso real pedido pelo dono: o hamburger vai para o
canto superior direito, o cartão grande do hub deixa de existir e entrar/sair
passa a ser uma ação do menu de perfis. O primeiro login pede o JSON do cliente
uma única vez; depois o fluxo é clicar → navegador → pronto.

## Fora de escopo

- Ler ou gravar planilhas no Drive (S9b).
- Exportar nas demais ferramentas (S9c).
- Embutir um cliente OAuth no repositório público.

## Decisões

- **Menu no conteúdo, não na sidebar:** uma faixa fina no topo da área de
  conteúdo alinha o hamburger à direita; a sidebar fica só com navegação e tema.
- **Sem cartão do Drive:** `drive_status` é removido. Login não é ferramenta e
  não ocupa o hub.
- **Menu de perfis:** sem conta, **Entrar com Google** com ícone de perfil; com
  contas, lista os e-mails com ícone e marca a ativa, além de **Adicionar
  conta** e **Sair desta conta**. Clicar em outro e-mail troca a conta.
- **Primeiro login:** se ainda não houver cliente OAuth, o clique em **Entrar
  com Google** abre o seletor nativo uma vez, importa o JSON validado e segue
  para o navegador. Depois disso o pedido não reaparece.
- **Estados no próprio menu:** “Conectando ao Google…”, erro de acesso negado,
  timeout e falha de cliente aparecem no menu, sem travar a navegação.

## Tarefas

1. Mover o `TopMenu` para uma faixa no topo do conteúdo, alinhada à direita.
2. Remover `drive_status` do hub, de `build_home` e dos testes.
3. Redesenhar os itens do menu: perfil, conta ativa, adicionar e sair.
4. Fazer o primeiro login pedir o cliente e então abrir o navegador.
5. Ajustar testes de sessão, shell, menu e tema.
6. Atualizar UI, arquitetura, setup, ADR 0018, roadmap, CHANGELOG e estado.
7. Fechar com lint, testes e docs verdes.

## Aceite

- [x] Hamburger no canto superior direito; sidebar sem o menu.
- [x] Nenhum cartão do Drive no hub.
- [x] Menu com ícone de perfil, perfis múltiplos, adicionar conta e sair.
- [x] Com cliente configurado, entrar abre o navegador direto.
- [x] Sem cliente, o primeiro clique pede o JSON uma vez e continua o login.
- [x] Testes, lint e docs verdes.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec e `ui/components/top_menu.py`.
Consultar `app.py`, `ui/pages/home.py`, `ui/drive.py` e
`ui/components/client_import.py` só no que o menu tocar.

## Arquivos prováveis

- `src/xl_utils/app.py`, `ui/components/sidebar.py`,
  `ui/components/top_menu.py`, `ui/pages/home.py`
- `ui/components/client_import.py`, `ui/drive.py`
- `tests/test_drive_session.py`, `tests/test_theme.py`
- `docs/reference/ui.md`, `docs/reference/architecture.md`,
  `docs/guide/setup.md`, `docs/adr/0018-drive-autenticacao.md`

## Riscos

- O seletor nativo pode não existir em ambiente headless; o teste cobre a
  sessão e a validação, não o diálogo do sistema.
- O primeiro login continua dependendo de o dono criar um cliente no Google
  Cloud; nenhum código contorna essa exigência do Google.
- O menu agora vive fora da sidebar; a troca de tema precisa recolori-lo
  explicitamente.

## Próximo depois desta

S9b — Drive II: link/seletor e escrita do resultado.
