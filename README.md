# Instagram Claude Skill Publisher

## Visão geral

Este projeto implementa uma skill para o Claude capaz de organizar e executar um fluxo automatizado de publicação de fotos no Instagram usando APIs oficiais.

A solução foi desenvolvida para atender a um desafio técnico com os seguintes requisitos:

- Execução 100% via API.
- Publicação de pelo menos uma foto com legenda em uma conta Instagram.
- Execução em background.
- Uso de app Meta em modo desenvolvimento/sandbox.
- Demonstração do funcionamento com prints ou vídeo.
- Proibição de automação via navegador, Selenium, Puppeteer, Playwright ou cliques simulados.

A arquitetura combina Claude Code Skill, Cloudinary API, fila local em JSON, worker Python em background e Instagram Graph API/Facebook Graph API.

---

## Arquitetura

```text
Claude Code Skill
↓
Script de enfileiramento
↓
Cloudinary API
↓
URL pública HTTPS da imagem
↓
Fila local JSON
↓
Worker Python em background
↓
Instagram Graph API / Facebook Graph API
↓
Post publicado no Instagram
```

A skill organiza o fluxo e define as regras da automação. O Cloudinary transforma uma imagem local em uma URL pública HTTPS. A fila JSON armazena publicações pendentes. O worker Python roda em background e processa automaticamente as publicações quando chega o horário configurado. A publicação final é feita pela Instagram Graph API/Facebook Graph API.

---

## Ferramentas utilizadas

- Claude Code Skills
- Python
- Cloudinary API
- Instagram Graph API / Facebook Graph API
- JSON como fila local
- Worker local em background
- Variáveis de ambiente com `.env`
- Git/GitHub para versionamento

---

## Requisitos atendidos

| Requisito | Status |
|---|---|
| Skill estruturada no Claude Code | Concluído |
| Execução via API oficial | Concluído |
| Upload de imagem via Cloudinary API | Concluído |
| Geração de URL pública HTTPS | Concluído |
| Fila JSON funcionando | Concluído |
| Worker em background funcionando | Concluído |
| Sem automação de navegador | Concluído |
| Sem Selenium, Puppeteer ou Playwright | Concluído |
| App Meta em desenvolvimento/sandbox | Concluído |
| Token real da Meta configurado | Concluído |
| Publicação real no Instagram | Concluído |
| Post publicado com legenda | Concluído |
| Evidências de funcionamento | Concluído |

---

## Estrutura do projeto

```text
PROJETO_ESTAGIO/
│
├── .claude/
│   └── skills/
│       └── instagram-publisher/
│           └── SKILL.md
│
├── scripts/
│   ├── cloudinary_client.py
│   ├── enqueue_post.py
│   ├── instagram_client.py
│   └── worker.py
│
├── data/
│   ├── posts_queue.json
│   └── posts_queue.example.json
│
├── docs/
│   ├── RELATORIO_DESAFIO.md
│   └── evidencias/
│
├── logs/
│   └── publisher.log
│
├── media/
│   └── test.jpg
│
├── .env
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Responsabilidade dos arquivos

### `.claude/skills/instagram-publisher/SKILL.md`

Arquivo principal da skill do Claude.

Define as regras de funcionamento do projeto, incluindo:

- Não usar automação via navegador.
- Não usar Selenium, Puppeteer, Playwright ou cliques simulados.
- Usar Cloudinary API para transformar imagem local em URL pública.
- Usar Instagram Graph API/Facebook Graph API para publicação.
- Usar worker Python para execução em background.

---

### `scripts/cloudinary_client.py`

Responsável por enviar a imagem local para o Cloudinary via API.

Entrada:

```text
media/test.jpg
```

Saída:

```text
https://res.cloudinary.com/...
```

A URL pública gerada pelo Cloudinary é usada como `image_url` na publicação do Instagram.

---

### `scripts/enqueue_post.py`

Responsável por criar uma nova tarefa de publicação.

Esse script:

```text
1. Recebe o caminho local da imagem.
2. Recebe a legenda.
3. Recebe a data e horário de agendamento.
4. Faz upload da imagem para o Cloudinary.
5. Recebe a URL pública HTTPS.
6. Cria um item na fila.
7. Salva a publicação em data/posts_queue.json.
```

Exemplo de uso:

```bash
python scripts/enqueue_post.py "media/test.jpg" "Publicado automaticamente via Claude Skill, Cloudinary API e Instagram Graph API." "2026-05-22T15:30:00"
```

---

### `data/posts_queue.json`

Arquivo usado como fila local de publicações.

Exemplo de item na fila:

```json
{
  "id": "uuid-do-post",
  "local_image_path": "media/test.jpg",
  "image_url": "https://res.cloudinary.com/...",
  "caption": "Legenda da publicação",
  "scheduled_at": "2026-05-22T15:30:00",
  "status": "pending",
  "created_at": "2026-05-22T15:25:00",
  "published_at": null,
  "cloudinary_public_id": "instagram_skill/post_...",
  "cloudinary_format": "jpg",
  "cloudinary_width": 1080,
  "cloudinary_height": 1080,
  "cloudinary_bytes": 123456,
  "creation_id": null,
  "media_id": null,
  "error": null
}
```

Principais status:

```text
pending          → publicação aguardando execução
mock_published   → publicação simulada em modo de desenvolvimento
published        → publicação real concluída no Instagram
failed           → erro durante a execução
```

---

### `scripts/worker.py`

Responsável por rodar em background.

O worker fica ativo verificando a fila em intervalos definidos e publica automaticamente os posts pendentes quando chega o horário configurado.

Fluxo do worker:

```text
1. Lê o arquivo data/posts_queue.json.
2. Procura posts com status pending.
3. Verifica se o horário scheduled_at já chegou.
4. Publica a imagem usando Instagram Graph API/Facebook Graph API.
5. Atualiza o status para published.
6. Registra logs da execução.
```

Comando para rodar:

```bash
python scripts/worker.py
```

---

### `scripts/instagram_client.py`

Responsável pela integração com a Instagram Graph API/Facebook Graph API.

No modo real, o fluxo usa dois endpoints principais:

```text
POST /{ig-user-id}/media
POST /{ig-user-id}/media_publish
```

Primeiro o sistema cria um container de mídia com a imagem e a legenda. Depois publica esse container no Instagram.

---

## Modos de execução

O projeto possui dois modos:

```text
Modo mock
Modo real
```

---

## Modo mock

O modo mock serve para desenvolvimento e testes.

No arquivo `.env`, use:

```env
MOCK_INSTAGRAM=true
```

Nesse modo:

- A imagem é enviada de verdade ao Cloudinary.
- A URL pública HTTPS é gerada.
- O post entra na fila JSON.
- O worker roda em background.
- A etapa final do Instagram é simulada.
- Nenhuma chamada real é feita ao Instagram.

Quando o modo mock funciona, o status muda para:

```text
mock_published
```

Esse modo não deve ser usado como evidência final de publicação no Instagram. Ele serve apenas para validar o fluxo enquanto a integração real com a Meta ainda não está configurada.

---

## Modo real

O modo real deve ser usado para a entrega final.

No arquivo `.env`, use:

```env
MOCK_INSTAGRAM=false
```

Também é necessário configurar:

```env
GRAPH_API_VERSION=v25.0
INSTAGRAM_USER_ID=seu_instagram_user_id
INSTAGRAM_ACCESS_TOKEN=seu_token_da_meta
```

Nesse modo:

- A imagem é enviada ao Cloudinary via API.
- A URL pública HTTPS é salva na fila.
- O worker roda em background.
- O worker chama a Instagram Graph API/Facebook Graph API.
- O post é publicado de verdade no Instagram.

Quando a publicação real funciona, o status muda para:

```text
published
```

---

## Configuração do ambiente

### 1. Criar ambiente virtual

```bash
python -m venv .venv
```

### 2. Ativar ambiente virtual no Windows

```bash
.\.venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Dependências

O arquivo `requirements.txt` deve conter:

```txt
requests
python-dotenv
cloudinary
```

---

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto.

Exemplo:

```env
# Cloudinary
CLOUDINARY_CLOUD_NAME=seu_cloud_name
CLOUDINARY_API_KEY=sua_api_key
CLOUDINARY_API_SECRET=seu_api_secret

# Meta / Instagram Graph API
GRAPH_API_VERSION=v25.0
INSTAGRAM_USER_ID=seu_instagram_user_id
INSTAGRAM_ACCESS_TOKEN=seu_token_da_meta

# Modo de execução
MOCK_INSTAGRAM=false

# Worker
QUEUE_FILE=data/posts_queue.json
WORKER_INTERVAL_SECONDS=15
```

O arquivo `.env` contém credenciais sensíveis e não deve ser enviado ao GitHub.

---

## Arquivo `.env.example`

O projeto contém um arquivo `.env.example` para demonstrar o formato esperado das variáveis sem expor credenciais reais.

Exemplo:

```env
# Cloudinary
CLOUDINARY_CLOUD_NAME=seu_cloud_name
CLOUDINARY_API_KEY=sua_api_key
CLOUDINARY_API_SECRET=seu_api_secret

# Meta / Instagram Graph API
GRAPH_API_VERSION=v25.0
INSTAGRAM_USER_ID=seu_instagram_user_id
INSTAGRAM_ACCESS_TOKEN=seu_token_da_meta

# Modo de execução
MOCK_INSTAGRAM=true

# Worker
QUEUE_FILE=data/posts_queue.json
WORKER_INTERVAL_SECONDS=15
```

---

## Segurança

O projeto usa `.gitignore` para impedir que credenciais e arquivos locais sensíveis sejam enviados ao GitHub.

O `.gitignore` deve conter:

```gitignore
# Ambiente virtual Python
.venv/

# Variáveis de ambiente com tokens e secrets
.env

# Cache do Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Logs locais
logs/*.log

# Arquivos do sistema
.DS_Store
Thumbs.db

# Arquivos temporários
*.tmp
*.bak

# Dados locais
data/posts_queue.json
```

Arquivos que não devem ir para o GitHub:

```text
.env
.venv/
data/posts_queue.json
logs/publisher.log
__pycache__/
```

Arquivos que podem ir para o GitHub:

```text
.env.example
README.md
requirements.txt
scripts/
.claude/
docs/
data/posts_queue.example.json
```

---

## Como adicionar uma publicação na fila

Use o comando:

```bash
python scripts/enqueue_post.py "CAMINHO_DA_IMAGEM" "LEGENDA" "AAAA-MM-DDTHH:MM:SS"
```

Exemplo:

```bash
python scripts/enqueue_post.py "media/test.jpg" "Publicado automaticamente via Claude Skill, Cloudinary API e Instagram Graph API." "2026-05-22T15:30:00"
```

O script vai:

```text
1. Localizar a imagem local.
2. Fazer upload para o Cloudinary.
3. Receber uma URL pública HTTPS.
4. Criar uma publicação com status pending.
5. Salvar a publicação em data/posts_queue.json.
```

---

## Como rodar o worker

Para rodar o worker no terminal:

```bash
python scripts/worker.py
```

O worker ficará ativo verificando a fila a cada intervalo configurado em:

```env
WORKER_INTERVAL_SECONDS=15
```

---

## Como rodar o worker em background no Windows

Para iniciar o worker em outra janela do PowerShell:

```powershell
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\.venv\Scripts\activate; python scripts\worker.py"
```

Esse comando inicia o worker em um processo separado, permitindo que ele continue verificando a fila sem intervenção manual.

---

## Como testar em modo mock

### 1. Ativar modo mock

No `.env`:

```env
MOCK_INSTAGRAM=true
```

### 2. Limpar a fila

No arquivo `data/posts_queue.json`, deixar:

```json
[]
```

### 3. Rodar o worker

```bash
python scripts/worker.py
```

### 4. Em outro terminal, adicionar uma publicação

```bash
python scripts/enqueue_post.py "media/test.jpg" "Teste em background com Cloudinary e modo mock." "2026-05-22T15:30:00"
```

### 5. Conferir o resultado

O worker deve processar a fila automaticamente.

O status esperado é:

```text
mock_published
```

---

## Como testar em modo real

### 1. Configurar o token da Meta

No `.env`:

```env
MOCK_INSTAGRAM=false
GRAPH_API_VERSION=v25.0
INSTAGRAM_USER_ID=seu_instagram_user_id
INSTAGRAM_ACCESS_TOKEN=seu_token_da_meta
```

### 2. Testar se o token está funcionando

```powershell
python -c "from dotenv import load_dotenv; import os, requests; load_dotenv(); v=os.getenv('GRAPH_API_VERSION','v25.0'); ig=os.getenv('INSTAGRAM_USER_ID'); token=os.getenv('INSTAGRAM_ACCESS_TOKEN'); r=requests.get(f'https://graph.facebook.com/{v}/{ig}', params={'fields':'id,username','access_token':token}); print(r.status_code); print(r.text)"
```

Resultado esperado:

```json
{
  "id": "ID_DA_CONTA_INSTAGRAM",
  "username": "usuario_instagram"
}
```

### 3. Limpar a fila

No arquivo `data/posts_queue.json`, deixar:

```json
[]
```

### 4. Adicionar uma publicação

```bash
python scripts/enqueue_post.py "media/test.jpg" "Publicado automaticamente via API oficial." "2026-05-22T15:30:00"
```

### 5. Rodar o worker

```bash
python scripts/worker.py
```

### 6. Conferir o resultado

O status esperado em `data/posts_queue.json` é:

```text
published
```

E o post deve aparecer na conta Instagram configurada.

---

## Fluxo da publicação real

O fluxo completo da publicação real é:

```text
1. Imagem local salva em media/test.jpg.
2. enqueue_post.py recebe imagem, legenda e horário.
3. Imagem é enviada ao Cloudinary via API.
4. Cloudinary retorna uma URL pública HTTPS.
5. Publicação é salva em data/posts_queue.json com status pending.
6. worker.py roda em background.
7. Worker identifica a publicação pendente.
8. Worker chama a Instagram Graph API.
9. A API cria o container de mídia.
10. A API publica o container.
11. A fila muda para status published.
12. O post aparece no Instagram.
```

---

## Evidências do desafio

As evidências foram organizadas em:

```text
docs/evidencias/
```

Evidências do fluxo estrutural e modo mock:

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

Evidências da publicação real:

```text
10_env_mock_false.png
11_worker_publicacao_real.png
12_fila_published.png
13_post_instagram.png
```

---

## Relatório técnico

O relatório técnico do desafio está em:

```text
docs/RELATORIO_DESAFIO.md
```

Ele descreve:

```text
1. Objetivo do projeto.
2. Ferramenta escolhida.
3. Arquitetura.
4. Justificativa do Cloudinary.
5. Justificativa do worker em background.
6. Estrutura do projeto.
7. Arquivos principais.
8. Modos de execução.
9. Evidências.
10. Requisitos atendidos.
11. Limitações e melhorias futuras.
```

---

## O que o projeto não usa

O projeto não usa:

```text
Selenium
Puppeteer
Playwright
Automação visual
Cliques simulados
Navegação automatizada no browser
```

A publicação é feita por API oficial.

---

## Limitações atuais

- A fila usa JSON local, suficiente para um MVP e para a demonstração do desafio.
- O worker roda localmente, então depende da máquina estar ligada.
- O token da Meta pode expirar dependendo do tipo de token utilizado.
- O projeto publica uma foto por vez.
- O projeto ainda não possui interface gráfica.
- O projeto não possui dashboard de gerenciamento de publicações.

---

## Melhorias futuras

Possíveis melhorias:

- Substituir JSON por banco de dados.
- Criar dashboard para gerenciar publicações.
- Adicionar suporte a carrossel.
- Adicionar suporte a reels.
- Criar sistema de retry automático.
- Implementar logs estruturados em JSON.
- Hospedar o worker em um servidor cloud.
- Criar validação automática de token.
- Adicionar testes automatizados.
- Criar endpoint HTTP para receber tarefas de publicação.
- Adicionar renovação ou alerta de expiração do token.

---

## Conclusão

O projeto implementa uma skill para Claude integrada a um fluxo automatizado de publicação no Instagram.

A solução usa APIs oficiais, não depende de automação de navegador, possui worker em background e realizou uma publicação real com legenda no Instagram.

A arquitetura separa responsabilidades de forma clara:

```text
Skill do Claude → orquestração
Cloudinary → hospedagem pública da imagem
JSON → fila local
Worker Python → execução em background
Instagram Graph API → publicação real
```

Com isso, o projeto demonstra integração com APIs, organização de arquitetura, execução autônoma, preocupação com segurança e documentação técnica para entrega.