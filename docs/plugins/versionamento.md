# Versionamento e compatibilidade

São três números independentes. Confundi-los é a causa mais comum de plugin que
instala e não carrega.

| Número | Onde | Quem muda | Para quê |
|---|---|---|---|
| `version` | `[plugin]` | autor do plugin | versão do próprio plugin |
| `api_version` | `[plugin]` | contrato do host | versão do manifesto, request/result e UI |
| `min_app_version` | `[plugin]` | autor do plugin | versão mínima do xl_Utils, quando a API não basta |

## `version` do plugin

SemVer `MAJOR.MINOR.PATCH`, sem pré-release nem build nesta versão:

- `PATCH`: correção sem mudar contrato nem comportamento esperado.
- `MINOR`: funcionalidade nova compatível.
- `MAJOR`: mudança que quebra quem depende do plugin.

O host exibe a versão e o `install.json` a registra. Duas versões do mesmo `id`
não convivem: instalar de novo é recusado; desinstale antes de trocar (a área
“Plugins” da S14 vai oferecer o fluxo).

## `api_version`

A API 1 cobre:

- os campos do `plugin.toml` e as regras de validação;
- `PluginRequest` e `PluginResult`;
- o schema de `[ui]` e `[[options]]`;
- o comportamento de instalação e descoberta.

O host declara o conjunto suportado; esta versão aceita `1`. Um manifesto com
outro valor é recusado com `unsupported_api`, sem tentativa de adaptação.

**Quebra de API** é qualquer mudança que faça um plugin válido na versão antiga
deixar de funcionar ou mudar de significado: campo obrigatório novo, remoção,
tipo diferente, default diferente, semântica diferente, schema de UI diferente.
Isso exige `api_version` novo. O host pode suportar mais de uma versão durante
uma transição.

Campos novos opcionais também exigem versão nova, porque o validador recusa
chaves desconhecidas de propósito. Preferimos erro cedo a campo ignorado em
silêncio.

## `min_app_version`

Use quando o plugin depende de um recurso do app que não está coberto pela API,
como uma correção de leitura ou uma tela nova. É um SemVer comparado com
`xl_utils.__version__`; se o app for mais antigo, a instalação falha com
`app_too_old`.

Na dúvida, prefira `api_version`: ela descreve o contrato, enquanto
`min_app_version` engessa a versão do produto. A versão que introduzir a área
“Plugins” (S14) é o marco inicial; use-a só quando necessário.

## `dependencies`

Lista de nomes de distribuições que o host deve ter, por exemplo
`["pandas", "openpyxl"]`. O host confere a presença com `importlib.metadata`;
não instala, não atualiza e não valida faixa de versão nesta API. Dependência
ausente falha com `missing_dependency`.

Dependência Python pura que o app não oferece deve ir dentro de `lib/`. Não
declare `pip`, `requirements.txt` ou instalação em tempo de execução.

## Compatibilidade na prática

| Situação | Resultado |
|---|---|
| Plugin API 1 em host API 1 | instala e carrega |
| Plugin API 1 em host API 2 | carrega se o host ainda suportar 1 |
| Plugin API 2 em host API 1 | recusa com `unsupported_api` |
| `min_app_version` maior que o app | recusa com `app_too_old` |
| Dependência ausente | recusa com `missing_dependency` |
| Campo desconhecido | recusa com `manifest_invalid` |

## Aposentadoria de uma API

Quando uma versão de API sair de moda, o host deve:

1. anunciar no `CHANGELOG` e no ADR;
2. manter a versão antiga por pelo menos uma release de transição;
3. avisar no carregamento qual versão ainda funciona;
4. remover só depois que os plugins conhecidos migrarem.

O repo privado de plugins deve fixar a faixa de `api_version` que testa e rodar
o validador do app no CI antes de publicar um pacote.

## Checklist de release do plugin

- [ ] `version` incrementada conforme a mudança.
- [ ] `api_version` correta para o host alvo.
- [ ] `min_app_version` só se realmente necessário.
- [ ] `plugin.toml` validado pelo CLI.
- [ ] Pacote `.tar.xz` e sidecar SHA-256 gerados juntos.
- [ ] Teste em pasta limpa: instalar, listar, desinstalar.
- [ ] CHANGELOG do plugin com a mudança.
