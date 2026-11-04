# ADR 0006 — Lote de arquivos nas ferramentas

- **Status:** aceita
- **Data:** 2026-11-04

## Contexto

As ferramentas de texto, CNJ e recorte nasceram lendo um único arquivo. O uso
real chega com várias planilhas do mesmo tipo, e selecionar uma por vez obriga a
repetir a mesma execução. O ADR 0005 definiu a seleção padrão de abas pensando no
merge: com vários arquivos, marca a primeira aba de cada um. Aplicar esse padrão
ao lote esconderia abas sem o usuário perceber.

## Decisão

- Todas as quatro ferramentas aceitam vários arquivos na entrada.
- Texto, CNJ e recorte processam **cada arquivo de forma independente**, com uma
  saída por origem em `output/`; a prévia prefixa o nome da aba com o arquivo e o
  log concatena as execuções.
- O merge continua sendo o único que junta os arquivos em uma saída.
- O padrão de abas depende da ferramenta:
  - lote (texto, CNJ, recorte): todas as abas de todos os arquivos;
  - merge: a primeira aba de cada arquivo, conforme o ADR 0005.
- A listagem de abas roda em thread; enquanto está pendente, o seletor mostra
  “Lendo as abas...” e o botão Executar fica desabilitado.
- Uma seleção vazia em qualquer arquivo bloqueia o lote inteiro com mensagem
  clara, antes de executar.

## Consequências

- O usuário pode limpar ou recortar um lote inteiro sem repetir a escolha.
- O resultado tem vários arquivos; “Abrir pasta” aponta para a pasta da primeira
  saída e o log lista todas.
- Falha de leitura no meio do lote interrompe a execução; as saídas já gravadas
  permanecem e aparecem no log.
- O merge mantém a regra antiga de seleção, agora como exceção documentada.
- `default_selection` ganha a opção `all_sheets` e os testes cobrem os dois modos.

## Alternativas

- **Manter uma planilha por execução:** simples, mas repete trabalho; rejeitado.
- **Concatenar automaticamente os arquivos:** é o papel do merge, não dos outros
  fluxos; rejeitado.
- **Usar a primeira aba de cada arquivo no lote:** silenciosamente perde abas;
  rejeitado.
- **Um único arquivo de saída por lote:** mistura origens sem a coluna `ORIGEM`;
  rejeitado.
