# S9b — Drive II: Picker, leitura e botão na entrada

## Objetivo

Ler uma planilha escolhida no Drive e entregá-la ao mesmo pipeline dos arquivos
locais, sem tocar em `output/`.

## Decisão tomada

Opção **(a) Google Picker**, mas pelo fluxo **desktop** documentado pelo Google:
uma autorização OAuth com `trigger_onepick=true` e retorno no loopback
`127.0.0.1`. Não há API key, JavaScript nem webview — o Flet 1.1.2 também não
tem `WebView`.

A requisição do Picker aceita só `drive.file`, então a escolha faz uma segunda
autorização curta, **sem** `access_type=offline` (para não acumular refresh
tokens que invalidam o login salvo). A concessão é por arquivo e por cliente; o
token da conta passa a enxergar o arquivo escolhido.

Pré-requisito no Cloud Console: **Google Picker API** ativa no mesmo projeto da
Drive API. Nenhum cliente novo, nenhuma API key, contas salvas intactas.

## Entregue

- Adendo ao ADR 0018 com o fluxo, o escopo único e a ausência de offline.
- `shared/drive_pick.py`: loopback efêmero, `state` e PKCE conferidos, retorno
  com `picked_file_ids` (um ou vários), cancelamento silencioso e timeout.
- `shared/drive.py`: metadados, download por `alt=media`, exportação de planilha
  nativa por `files.export`, refresh único em 401 e erros em PT-BR (403, 404,
  cota, exportação acima de 10 MB e Google ocupado).
- `shared/drive_cache.py`: cópia temporária com nome real em
  `%LOCALAPPDATA%/xl_utils/drive/cache/<sessão>/`, limpa na abertura do app.
- `ui/drive.py`: `open_from_drive`, com o Picker e o download fora da UI thread.
- `FileInput`: botão quadrado do Drive na mesma linha da dropzone, só com conta;
  uma conta abre direto, duas ou mais pedem qual; o arquivo fica ligado à conta
  escolhida.
- “Salvar em `output/`” recusa entrada do Drive e manda usar “Salvar” com
  destino escolhido.
- Script manual `scripts/check-drive-picker.py`.

## Aceite

- [x] Planilha do Drive escolhida no Picker entra no pipeline como local.
- [x] Planilha nativa do Google é exportada como `.xlsx`.
- [x] Cancelar não vira erro; 403/404/cota viram mensagem clara.
- [x] Token expirado renova uma vez; o token nunca aparece em mensagem.
- [x] Testes offline verdes; ferramentas locais intactas.
- [x] Botão aparece e some conforme as contas; múltiplas contas perguntam antes.

## Fica para a S9c

Gravar o resultado no Drive, dentro da pasta de origem, com a concessão da pasta
guardada por conta; “Salvar no Drive” no painel de resultado; exportação nas
demais ferramentas.

## Riscos que sobraram

- A pasta do arquivo escolhido **não** vem concedida: gravar nela exigirá uma
  escolha de pasta do usuário (ver S9c).
- O fluxo desktop do Picker é novo; o teste manual com conta real é o juiz.
- Exportação de planilha nativa tem limite de 10 MB no Google.
