# S11 — Versão 0.2.0 e polimento de UI

## Objetivo

Marcar o app como **0.2.0** e corrigir os dois estouros de layout conhecidos:
cartões do Início/páginas em largura estreita e e-mail longo no menu de perfis.

## Fora de escopo

- Instalador, wheel, Python embutido ou qualquer empacotamento (fica na S12).
- Plugins, seletor próprio de arquivos e mudança de escopo do Drive.
- Redesenho do Início, da sidebar ou do tema; só o que estoura é ajustado.

## Tarefas

1. Achar toda ocorrência de `0.1.0` (grep em `pyproject.toml`,
   `src/xl_utils/__init__.py`, diagnóstico, docs e testes), trocar para
   `0.2.0` e rodar `uv lock` para o lock acompanhar.
2. Reproduzir o estouro com a janela estreita: no Início e em **Verificar
   Vínculos**, o título quebra no meio da palavra, a descrição vaza do cartão e
   “Abrir ferramenta” sai da área visível.
3. Corrigir o cartão (`ui/pages/home.py`, `ui/pages/registry.py`): largura
   mínima/máxima que respeite o container, descrição truncada com `…` e atalho
   sempre dentro do cartão; nada de overflow horizontal na página.
4. Truncar o e-mail no menu de perfis (`ui/components/top_menu.py`) com `…` e
   oferecer o valor completo em tooltip com atraso de hover de 2–3 s; revisar
   qualquer outro ponto que exiba e-mail.
5. Cobrir com teste headless: cartão sem estouro numa largura estreita e e-mail
   truncado/tooltip configurado.
6. Atualizar `CHANGELOG.md`, `docs/state/CURRENT.md` e `docs/reference/ui.md`
   (seção de layout) e escrever a spec da próxima sessão.

## Aceite

- [ ] `0.2.0` em `pyproject.toml`, `__init__.py`, lock, diagnóstico e docs.
- [ ] Início e Verificar Vínculos sem estouro em ~960 px, nos dois temas.
- [ ] E-mail longo vira `…` no item e o completo aparece só no tooltip.
- [ ] `ruff`, `pytest` e `node scripts/check-docs.mjs` verdes.
- [ ] Validação visual no app em largura cheia e estreita.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec e, só quando for editar, os três
arquivos de UI citados. Não abrir os controllers nem o core: a sessão não muda
regra de negócio.

## Arquivos prováveis

- `pyproject.toml`, `uv.lock`, `src/xl_utils/__init__.py`
- `src/xl_utils/ui/pages/home.py`, `src/xl_utils/ui/pages/registry.py`
- `src/xl_utils/ui/components/top_menu.py`, `src/xl_utils/ui/theme.py`
- `docs/reference/ui.md`, `CHANGELOG.md`, `docs/state/CURRENT.md`
- `tests/` (novo teste de UI headless)

## Riscos

- Tooltip do Flet não tem atraso nativo: pode ser preciso um `Timer` no hover;
  se não houver evento confiável, registrar a limitação e usar o tooltip padrão.
- Largura fixa em pixels quebra em telas grandes; usar mínimo/máximo e testar
  em duas larguras.
- `uv lock` pode subir dependências de propósito; conferir se o lock muda só a
  versão do projeto e rodar a suíte.

## Próximo depois desta

**S12 — empacotar a primeira versão, 0.3.0**, com instalador Windows, Python
embutido e publicação do artefato nas Releases.
