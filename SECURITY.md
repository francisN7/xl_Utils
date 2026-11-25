# Segurança

## Versões suportadas

Só a última release publicada em
[Releases](https://github.com/francisN7/xl_Utils/releases) e a branch `main`
recebem correções. A branch `legacy` não recebe manutenção.

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

- Leitura de `.xlsx`, `.xlsm`, `.xls`, `.csv` e `.html` e gravação de saídas.
- Aplicativo desktop local. A rede só é usada pelo Google Drive, que é
  opcional: login OAuth, Picker, download e upload, sempre em `https://` para
  domínios do Google e com retorno em `127.0.0.1`. O escopo é `drive.file`: o
  app só enxerga o que criou ou o que o usuário escolheu.
- Token do Drive protegido por DPAPI no Windows e pelo chaveiro do sistema no
  Linux (ADR 0030); o segredo do cliente OAuth também usa DPAPI no Windows. O
  repositório nunca carrega cliente OAuth, token ou conta real.
- Instalação de plugins: validação do pacote `.tar.xz` (caminhos, binários,
  limites e SHA-256). O plugin em si roda no mesmo processo, sem sandbox; o que
  ele faz depois de instalado é responsabilidade de quem o instala (ver
  [`docs/plugins/permissoes-e-seguranca.md`](docs/plugins/permissoes-e-seguranca.md)).

## Fora de escopo

- Planilhas malformadas usadas como prova de conceito sem impacto claro.
- Engenharia social, ataques físicos e problemas no ambiente do usuário.

## Prazo

Resposta inicial em até 7 dias. A correção depende da gravidade e da
disponibilidade do mantenedor.
