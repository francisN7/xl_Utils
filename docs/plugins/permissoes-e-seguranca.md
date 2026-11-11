# Permissões e segurança

O plugin roda **no mesmo processo** do xl_Utils, com os direitos do usuário que
abriu o app. Não existe sandbox nesta versão. Instalar um plugin é um ato de
confiança no código dele, como instalar uma extensão de editor ou um pacote de
um repositório que você escolheu.

O instalador reduz a superfície do **pacote**: impede caminhos maliciosos,
symlinks, binários nativos e zip bombs, e confere o hash. Ele não controla o que
o código faz depois de carregado.

## Permissões declaradas

O manifesto declara:

```toml
[permissions]
network = false
filesystem = "read"   # none | read | write
subprocess = false
```

Essas chaves são **informação para o usuário e para a revisão do plugin**, não
um mecanismo de bloqueio. Um plugin que declara `network = false` e abre um
socket não é impedido pelo host; ele quebra a promessa e deve ser tratado como
não confiável.

A UI da S14 deve mostrar as permissões no momento de instalar ou abrir o plugin.
Nesta sessão, o validador só confere tipo e valor; a exibição vem com a área
“Plugins”.

## O que o instalador garante

- O `plugin.toml` existe, é válido e compatível com a API.
- O pacote é `.tar.xz`, tem sidecar SHA-256 e não passa dos limites.
- Nenhum caminho escapa da pasta de instalação: sem absoluto, `..`, unidade,
  barra invertida, dois-pontos, controle, nome reservado ou colisão de caixa.
- Só entram arquivo regular e diretório; symlink, hardlink, FIFO, dispositivo e
  sparse são recusados.
- Nenhum binário nativo ou instalador de dependência entra no pacote.
- O id não sobrescreve um plugin existente.
- O código do plugin **não é importado** durante a validação, a instalação, a
  descoberta ou a desinstalação.
- A promoção para `plugins/<id>/` é atômica; falha não deixa pasta parcial.

## O que o instalador não garante

- Que o plugin não leia ou grave fora da pasta dele.
- Que o plugin não use rede, subprocesso, clipboard ou memória sem limite.
- Que o plugin não derrube o processo ou trave a UI.
- Que o hash prove autoria: o sidecar detecta corrupção e arquivo errado, mas
  não uma substituição maliciosa do pacote e do sidecar juntos.
- Que o código seja livre de vulnerabilidades; não há análise estática nem
  assinatura de código nesta versão.

## Limites do pacote

| Item | Limite |
|---|---:|
| Arquivo `.tar.xz` | 100 MB |
| Conteúdo extraído | 500 MB |
| Entradas no tar | 10.000 |
| Arquivo individual | 200 MB |
| Razão extraído/pacote | 500:1 |
| Nome de entrada | 180 caracteres |
| Caminho final | 250 caracteres |
| `plugin.toml` | 256 KB |
| Memória do xz | 256 MB |

Os números são generosos, mas o limite de conteúdo extraído e a razão barram
um zip bomb antes de encher o disco. O host também confere o espaço livre e
aborta a extração ao passar do teto, mesmo que o cabeçalho do tar minta.

## Regras para o autor

- Declare as permissões de verdade; não peça o que não usa.
- Não colete dados pessoais nem envie planilhas para servidores sem o usuário
  saber.
- Não registre conteúdo de célula no log, no progresso ou em arquivo de
  diagnóstico.
- Traga dependências Python puras dentro de `lib/` ou declare pacotes que o app
  já oferece; não dependa de `pip` no momento da instalação.
- Trate erros e respeite `request.cancel.cancelled`; não use `os._exit`.
- Guarde dados em `request.data_dir`, nunca em `plugins/<outro-id>/` nem em
  pastas do sistema. A desinstalação apaga `data/`.

## Regras para quem instala

- Instale só pacotes de origem conhecida.
- Leia o `plugin.toml` e as permissões; o sidecar só confirma integridade.
- Desconfie de pacote que pede `filesystem = "write"`, `subprocess = true` ou
  `network = true` sem uma razão clara.
- A desinstalação apaga os dados do plugin; exporte o que quiser manter.

## Próximos passos de segurança

Subprocesso com protocolo JSON e, depois, sandbox de verdade no Windows
(AppContainer/Job Object) são decisões futuras, não promessas desta API.
Assinatura de código e um catálogo confiável também ficam para outro ciclo. O
ADR 0023 registra o risco e a alternativa.
