# Relatório do Desafio — Instagram Claude Skill Publisher

## 1. Objetivo

O objetivo deste projeto é criar uma skill para o Claude capaz de organizar e executar um fluxo automatizado de publicação de fotos no Instagram usando APIs oficiais.

A solução foi pensada para atender aos seguintes requisitos:

- Publicação via Instagram Graph API/Facebook Graph API.
- Sem uso de Selenium, Puppeteer, Playwright ou automação de navegador.
- Execução em background.
- Uso de app Meta em modo desenvolvimento/sandbox.
- Publicação de pelo menos uma foto com legenda.
- Demonstração por prints ou vídeo.

---

## 2. Ferramenta escolhida

A ferramenta escolhida foi Claude Code Skills.

A escolha foi feita porque esse formato permite estruturar uma skill com instruções próprias, regras de execução, scripts auxiliares e um fluxo claro de automação.

A skill fica localizada em:

```text
.claude/skills/instagram-publisher/SKILL.md
```

---

## 3. Arquitetura da solução

A arquitetura do projeto foi dividida em camadas:

```text
Claude Skill
↓
Script de enfileiramento
↓
Cloudinary API
↓
Fila local JSON
↓
Worker Python em background
↓
Instagram Graph API / Facebook Graph API
↓
Post publicado no Instagram
```

A skill é responsável por organizar o fluxo. O Cloudinary é usado para transformar uma imagem local em uma URL pública HTTPS. A fila JSON armazena as publicações pendentes. O worker Python fica rodando em background e processa as publicações automaticamente.

---

## 4. Motivo do uso do Cloudinary

A Instagram Graph API não recebe diretamente arquivos locais como `media/test.jpg`.

Por isso, antes de publicar no Instagram, o projeto envia a imagem local para o Cloudinary via API. O Cloudinary retorna uma URL pública HTTPS, que pode ser usada como `image_url` na chamada da Instagram Graph API.

Fluxo:

```text
media/test.jpg
↓
Cloudinary API
↓
https://res.cloudinary.com/...
↓
Instagram Graph API
```

---

## 5. Motivo do uso de worker em background

A skill do Claude organiza e orienta a execução, mas o processamento autônomo é feito pelo worker.

O worker é necessário porque o desafio exige que a solução rode em background, ou seja, sem intervenção manual durante a execução.

O arquivo responsável por isso é:

```text
scripts/worker.py
```

Ele verifica a fila periodicamente, identifica publicações pendentes e executa a publicação quando chega o horário configurado.

---

## 6. Modo mock de desenvolvimento

Durante o desenvolvimento, foi implementado um modo mock controlado pela variável:

```env
MOCK_INSTAGRAM=true
```

Nesse modo:

- a imagem é enviada de verdade ao Cloudinary;
- a URL pública é gerada de verdade;
- a publicação entra de verdade na fila;
- o worker roda de verdade em background;
- a etapa final do Instagram é simulada.

Esse modo não substitui a publicação real exigida no desafio. Ele serve apenas para validar o fluxo enquanto o acesso ao Meta Developers/token da Meta ainda está pendente.

Para a entrega final, será usado:

```env
MOCK_INSTAGRAM=false
```

com `INSTAGRAM_USER_ID` e `INSTAGRAM_ACCESS_TOKEN` reais.

---

## 7. Arquivos principais

### Skill

```text
.claude/skills/instagram-publisher/SKILL.md
```

Define as regras da skill, incluindo a proibição de automação via navegador.

### Upload Cloudinary

```text
scripts/cloudinary_client.py
```

Faz upload da imagem local para o Cloudinary via API.

### Enfileiramento

```text
scripts/enqueue_post.py
```

Recebe imagem, legenda e horário. Envia a imagem para o Cloudinary e adiciona a publicação na fila.

### Worker

```text
scripts/worker.py
```

Roda em background, verifica a fila e processa publicações pendentes.

### Cliente Instagram

```text
scripts/instagram_client.py
```

No modo real, chama a Instagram Graph API/Facebook Graph API.

---

## 8. Requisitos atendidos até o momento

| Requisito | Status |
|---|---|
| Skill estruturada no Claude Code | Concluído |
| Upload de imagem via API | Concluído |
| Cloudinary gerando URL pública HTTPS | Concluído |
| Fila JSON funcionando | Concluído |
| Worker em background funcionando | Concluído |
| Sem automação de navegador | Concluído |
| Modo mock para desenvolvimento | Concluído |
| Token real da Meta | Pendente |
| Publicação real no Instagram | Pendente |

---

## 9. Pendência para entrega final

A única etapa pendente para a entrega final é configurar o app no Meta Developers, obter o `INSTAGRAM_USER_ID` e o `INSTAGRAM_ACCESS_TOKEN`, alterar `MOCK_INSTAGRAM=false` e realizar uma publicação real usando a Instagram Graph API.

Depois disso, o status esperado na fila será:

```text
published
```

E o post deverá aparecer na conta Instagram configurada.

---

## 10. Evidências esperadas

As evidências do funcionamento ficam na pasta:

```text
docs/evidencias/
```

Lista de evidências:

```text
01_estrutura_projeto.png
02_skill_claude.png
03_cloudinary_client.png
04_enqueue_post.png
05_worker_background.png
06_fila_pending.png
07_worker_processando.png
08_fila_mock_published.png
09_github_repositorio.png
```