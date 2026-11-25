# ADR 0032 — AppImage como formato da versão Linux

- **Status:** aceita
- **Data:** 2026-11-25

## Contexto

A 0.4.0 sai para Windows e Linux (S23a–c). O Windows já usa `flet pack` com
Inno Setup. O Linux precisa de um arquivo que o dono gere na máquina dele, que
rode em mais de uma distro e que não peça root para instalar.

## Decisão

- **Formato:** AppImage x86_64, montado a partir do bundle onedir do
  `flet pack`, o mesmo caminho do Windows (`scripts/build_linux.sh`).
- **Ferramentas fixadas:** `appimagetool` 1.9.1 e o runtime type2 `20251108`,
  com SHA-256 no script e conferência antes de executar. O runtime vai por
  `--runtime-file`, para o `appimagetool` não buscar o `continuous` na rede.
- **Keyring:** `--copy-metadata keyring` e `--collect-submodules
  keyring.backends`, mais `secretstorage` e `jeepney`. O build falha se algum
  deles ficar fora do bundle, para o login não sumir sem aviso (ADR 0030).
- **Piso:** glibc 2.39 (Ubuntu 24.04+). Esse piso vem do cliente Flet embutido
  (`ubuntu24.04-light`) e do `libstdc++` da máquina de build.
- **Identidade da janela:** `StartupWMClass=com.appveyor.flet`, porque o
  cliente Flet 1.1.x ignora o `FLET_APP_ID`. Trocar quando o Flet corrigir.

## Alternativas descartadas

- **`flet build linux`:** exige o SDK do Flutter e gera outro app. Seriam dois
  caminhos de build para manter.
- **`.deb`/`.rpm`:** um pacote por família de distro e instalação com root.
- **Flatpak:** sandbox do portal para arquivos e chaveiro, manifesto e
  runtime próprios, e publicação no Flathub. É custo demais para um usuário.
- **Tarball do bundle:** funciona, mas sem ícone, `.desktop` nem arquivo único.
- **`appimagetool` `continuous`:** muda sem aviso e não dá para fixar o hash.

## Consequências

- O build é reproduzível na versão das ferramentas, mas não bit a bit: o
  bundle embute o `libstdc++` da máquina de build.
- Distros com glibc mais velha ficam fora. Para cobri-las, seria preciso
  buildar num contêiner antigo (S23b pode reavaliar).
- O `--web` não funciona no executável, como no Windows.
