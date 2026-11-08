# S9a3 — Site público e política de privacidade

## Objetivo

Destravar a publicação do app OAuth no Google Cloud: o modo “Em produção”
(externo) exige URL de página inicial e de política de privacidade. O
repositório passa a publicar um site estático mínimo no GitHub Pages, com a
apresentação do app e a política de privacidade.

## Fora de escopo

- Instalador, release e download do app.
- Verificação de marca do Google (opcional para escopos não sensíveis).
- Coleta de métricas ou formulário de contato próprio.

## Decisões

- **GitHub Pages a partir de `docs/`:** sem serviço novo e sem custo; o site
  usa o mesmo repositório público.
- **Só o site é publicado:** `docs/_config.yml` exclui `adr`, `guide`,
  `reference`, `roadmap`, `sessions`, `state` e `README.md` do Jekyll. Os
  documentos internos continuam no Git, mas não viram páginas.
- **HTML estático e autocontido:** sem tema, CDN ou dependência externa; o
  visual segue o Dracula do app.
- **Política em PT-BR:** descreve escopos (`openid`, `email`, `drive.file`),
  armazenamento local com DPAPI, ausência de servidor/telemetria, exclusão,
  revogação e conformidade com a Google API Services User Data Policy
  (Limited Use).
- **Endereços:** home em `https://francisn7.github.io/xl_Utils/` e política em
  `.../privacy.html`; domínio autorizado `francisn7.github.io`.

## Tarefas

1. Criar `docs/index.html` com a apresentação e os links.
2. Criar `docs/privacy.html` com a política completa.
3. Criar `docs/_config.yml` com a lista de exclusão do Pages.
4. Ligar as páginas no mapa da documentação.
5. Validar docs, lint e testes; commitar e enviar.

## Aceite

- [x] Home e política acessíveis por GitHub Pages em `docs/`.
- [x] Documentos internos fora do site publicado.
- [x] Política cobre escopos, armazenamento, exclusão e Limited Use.
- [x] Docs, lint e testes verdes.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec e `docs/README.md`. Só abrir
`docs/index.html` e `docs/privacy.html` se for editar o texto.

## Arquivos prováveis

- `docs/index.html`, `docs/privacy.html`, `docs/_config.yml`
- `docs/README.md`, `docs/roadmap/main.md`, `docs/state/CURRENT.md`,
  `CHANGELOG.md`

## Riscos

- GitHub Pages leva alguns minutos para o primeiro deploy; o Google pode
  recusar a URL enquanto ela não responder.
- O nome do app no consentimento precisa ser válido; usar “xl Utils” evita
  problema com o sublinhado.
- A política é declaratória: se o app passar a enviar dados a um servidor, o
  texto e a classificação de escopos precisam ser revistos.

## Próximo depois desta

S9b — Drive II: link/seletor e escrita do resultado.
