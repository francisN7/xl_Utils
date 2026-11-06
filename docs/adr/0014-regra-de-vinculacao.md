# ADR 0014 — Vinculação por valor bruto

- **Status:** aceita
- **Data:** 2026-11-06

## Contexto

A quinta ferramenta cruza AGENDA, FINANCEIRO, CLIENTES e PROCESSOS para
responder se uma linha encontrou o processo correspondente. As planilhas vêm
de sistemas diferentes e os mesmos campos aparecem com máscara, zeros, espaços
e grafias variadas. O dono pediu explicitamente que a ferramenta funcione como
um **teste de vinculação**: comparar o que está na planilha, não “consertar” o
valor para forçar um match.

Ao mesmo tempo, um CNJ fora do padrão não pode passar em silêncio: se o campo
estiver preenchido e não for nem a máscara canônica nem 20 dígitos contínuos, a
execução inteira para e lista os casos.

## Decisão

- **Comparação bruta.** CNJ, PASTA, PROTOCOLO e nome são comparados caractere a
  caractere, sem trim, sem colapso de espaço, sem remover zeros e sem juntar
  formatos. Máscara × 20 dígitos **não vincula**; é o comportamento esperado.
- **Validação de CNJ.** Aceita exatamente `NNNNNNN-NN.NNNN.N.NN.NNNN` ou
  `NNNNNNNNNNNNNNNNNNNN` (20 dígitos). Campo vazio é permitido. Qualquer outro
  valor preenchido levanta `InvalidCnjError`, que carrega todos os casos com
  arquivo, aba, linha, coluna e valor; nada é gravado.
- **Prioridade.** CNJ → PASTA → PROTOCOLO, parando no primeiro vínculo. O
  resultado é `VINCULA POR CNJ`, `VINCULA POR PASTA` ou
  `VINCULA POR PROTOCOLO`; sem vínculo, `NÃO vincula, apenas processo
  consultivo`.
- **AGENDA sem vínculo.** O valor do protocolo é preservado na descrição como
  `<CABEÇALHO REAL>: <valor>`, separado por quebra de linha; o campo de
  protocolo vira `MIGRAÇÃO`, mesmo quando o protocolo está vazio. Se a descrição
  estiver vazia, entra só a linha do protocolo.
- **Reexecução.** Se a coluna de protocolo da AGENDA já contém `MIGRAÇÃO`, a
  página avisa e pergunta. Confirmando, `VINCULA?` é recalculado e a linha do
  protocolo **não** é acrescentada de novo à descrição. O núcleo também recusa
  a reexecução sem `allow_migrated`, para proteger chamadas fora da UI.
- **Cabeçalhos.** O casamento do rótulo dobra caixa, acento e espaço
  (`fold_header`); os valores das células continuam brutos. O match é exato,
  não por substring, para não confundir `PROCESSO ORIGINÁRIO` com `PROCESSO`.
- **Colunas novas.** Entram depois do último rótulo do bloco padrão e antes das
  extras. Se a coluna já existir, é sobrescrita no lugar, sem duplicar. Todas
  as colunas de entrada e as outras abas são preservadas.
- **Configuração.** Os rótulos padrão vivem em `headers.json` (ver ADR 0015); a
  regra recebe o mapa por parâmetro e não lê arquivo.

## Consequências

- O falso negativo por formato diferente é intencional e visível: o log conta
  quantos CNJs vieram mascarados e quantos vieram crus em cada planilha.
- Planilha com CNJ numérico pode perder precisão antes da leitura (o Excel
  guarda 15 dígitos significativos). A ferramenta não consegue recuperar o
  valor; a orientação é manter a coluna como texto.
- O erro de CNJ é global: uma única linha inválida impede a gravação de toda a
  saída, como pedido.
- A descrição da AGENDA cresce com a linha do protocolo; rodar de novo no
  arquivo de saída não duplica essa linha.
- A regra é pura e testável sem Flet; a página só coleta arquivos e mostra o
  resultado.

## Alternativas

- **Normalizar CNJ e remover pontuação:** aumentaria os matches, mas esconderia
  o problema que o teste quer revelar.
- **Aceitar qualquer texto no CNJ e só não vincular:** contraria o pedido de
  parar tudo e avisar.
- **Mover o protocolo para uma coluna nova em vez da descrição:** a migração
  viraria um campo que o sistema de destino não conhece; a descrição é o único
  lugar editável.
- **Comparar nome com tolerância a caixa/acento:** fica fora desta decisão;
  quando entrar, será uma opção explícita e documentada.
