# Segurança

## Versões suportadas

Apenas a versão atual da branch `main` recebe correções. O projeto está em
`0.1.x` e ainda não publica releases.

## Como relatar

Use o **relato privado de vulnerabilidades** do GitHub: aba **Security** →
**Report a vulnerability**. Não abra issue pública para falhas de segurança.

Inclua, quando possível:

- versão do app, do Python e do sistema;
- passos para reproduzir com um arquivo fictício;
- impacto observado (leitura indevida, gravação fora do destino, travamento,
  execução de código etc.);
- log ou traceback sem dados de célula.

Nunca anexe planilha com dados reais, CPF/CNPJ, credenciais, tokens ou caminhos
pessoais.

## Escopo

- Leitura de `.xlsx`, `.xls`, `.csv` e `.html` e gravação de saídas.
- Aplicativo desktop local, sem servidor e sem chamadas de rede nesta versão.
- A integração com o Google Drive (S9a) ainda não está implementada.

## Fora de escopo

- Planilhas malformadas usadas como prova de conceito sem impacto claro.
- Engenharia social, ataques físicos e problemas no ambiente do usuário.

## Prazo

Resposta inicial em até 7 dias. A correção depende da gravidade e da
disponibilidade do mantenedor.
