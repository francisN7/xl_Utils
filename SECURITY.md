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
- Aplicativo desktop local. A única chamada de rede é o login OAuth do Google
  Drive (S9a), sempre em `https://` para domínios do Google e com retorno em
  `127.0.0.1`; a leitura e a gravação de planilhas no Drive ainda não existem.
- Tokens do Drive protegidos por DPAPI; o repositório nunca carrega cliente
  OAuth, token ou conta real.

## Fora de escopo

- Planilhas malformadas usadas como prova de conceito sem impacto claro.
- Engenharia social, ataques físicos e problemas no ambiente do usuário.

## Prazo

Resposta inicial em até 7 dias. A correção depende da gravidade e da
disponibilidade do mantenedor.
