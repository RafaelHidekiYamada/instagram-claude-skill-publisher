# Instagram Claude Skill Publisher

## Visão geral

Este projeto implementa uma skill para o Claude capaz de organizar o fluxo de publicação automática de fotos no Instagram usando APIs oficiais.

A solução foi construída para atender a um desafio técnico com os seguintes requisitos principais:

- Publicar conteúdo no Instagram via API.
- Não usar automação de navegador.
- Rodar em background.
- Usar um app Meta em modo desenvolvimento/sandbox.
- Demonstrar o funcionamento com prints ou vídeo.
- Publicar pelo menos uma foto com legenda em uma conta Instagram.

O projeto utiliza uma arquitetura composta por:

```text
Claude Skill
↓
Upload da imagem local para o Cloudinary via API
↓
Geração de URL pública HTTPS
↓
Fila local em JSON
↓
Worker Python rodando em background
↓
Instagram Graph API / Facebook Graph API
↓
Publicação no Instagram
```

---

## Ferramentas utilizadas

- Claude Code Skills
- Python
- Cloudinary API
- Instagram Graph API / Facebook Graph API
- JSON como fila local
- Worker local em background
- Arquivo `.env` para variáveis de ambiente

---

## Objetivo do projeto

O objetivo é permitir que uma imagem local seja preparada para publicação no Instagram de forma automatizada.

Como a Instagram Graph API exige uma URL pública da imagem, o sistema primeiro envia a imagem local para o Cloudinary. O Cloudinary retorna uma URL HTTPS pública, que depois é usada pelo worker para publicar a foto no Instagram.

A skill do Claude atua como camada de orquestração, enquanto o worker Python é responsável pela execução autônoma em background.

---

## Arquitetura

```text
+--------------------------+
| Claude Code Skill        |
| instagram-publisher      |
+------------+-------------+
             |
             | agenda/cria tarefa
             v
+--------------------------+
| enqueue_post.py          |
| recebe imagem e legenda  |
+------------+-------------+
             |
             | upload via API
             v
+--------------------------+
| Cloudinary API           |
| retorna secure_url       |
+------------+-------------+
             |
             | salva URL pública
             v
+--------------------------+
| posts_queue.json         |
| status: pending          |
+------------+-------------+
             |
             | worker verifica fila
             v
+--------------------------+
| worker.py                |
| execução em background   |
+------------+-------------+
             |
             | chamada via API
             v
+--------------------------+
| Instagram Graph API      |
| /media e /media_publish  |
+------------+-------------+
             |
             v
+--------------------------+
| Foto publicada           |
| no Instagram             |
+--------------------------+
```

---

## Estrutura do projeto

```text
instagram-claude-skill/
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
│   └── posts_queue.json
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
├── requirements.txt
└── README.md
```

---

## Responsabilidade dos arquivos

### `.claude/skills/instagram-publisher/SKILL.md`

Arquivo principal da skill do Claude.

Ele define quando a skill deve ser usada, quais regras devem ser seguidas e como o fluxo de publicação deve funcionar.

A skill deixa explícito que:

- não deve usar navegador;
- não deve usar Selenium, Puppeteer ou Playwright;
- deve usar Cloudinary API para hospedar a imagem;
- deve usar Instagram Graph API/Facebook Graph API para publicar;
- deve usar o worker para execução em background.

---

### `scripts/cloudinary_client.py`

Responsável por fazer upload da imagem local para o Cloudinary via API.

Entrada:

```text
media/test.jpg
```

Saída:

```text
https://res.cloudinary.com/...
```

Essa URL pública é necessária porque a Instagram Graph API não aceita arquivos locais diretamente. Ela precisa receber uma URL pública acessível pela internet.

---

### `scripts/enqueue_post.py`

Responsável por criar uma nova publicação na fila.

Ele executa as seguintes etapas:

1. Recebe o caminho local da imagem.
2. Recebe a legenda.
3. Recebe o horário de agendamento.
4. Envia a imagem para o Cloudinary.
5. Recebe a URL pública da imagem.
6. Salva a publicação no arquivo `data/posts_queue.json`.

Exemplo de uso:

```bash
python scripts/enqueue_post.py "media/test.jpg" "Legenda da publicação" "2026-05-20T21:30:00"
```

---

### `data/posts_queue.json`

Arquivo usado como fila local de publicações.

Exemplo de item na fila:

```json
[
  {
    "id": "uuid-do-post",
    "local_image_path": "media/test.jpg",
    "image_url": "https://res.cloudinary.com/...",
    "caption": "Legenda da publicação",
    "scheduled_at": "2026-05-20T21:30:00",
    "status": "pending",
    "created_at": "2026-05-20T21:25:00",
    "published_at": null,
    "cloudinary_public_id": "instagram_skill/post_...",
    "creation_id": null,
    "media_id": null,
    "error": null
  }
]
```

Principais status:

```text
pending          → publicação aguardando execução
mock_published   → execução simulada com sucesso em modo de desenvolvimento
published        → publicação real feita no Instagram
failed           → erro durante a execução
```

---

### `scripts/worker.py`

Responsável por rodar em background.

O worker verifica a fila periodicamente e publica automaticamente os posts pendentes quando chega o horário agendado.

Fluxo do worker:

```text
1. Lê o arquivo posts_queue.json.
2. Procura posts com status pending.
3. Verifica se o horário scheduled_at já chegou.
4. Publica a imagem usando Instagram Graph API.
5. Atualiza o status da publicação.
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

Primeiro é criado um container de mídia com a imagem e a legenda. Depois esse container é publicado no Instagram.

---

## Modos de execução

O projeto possui dois modos:

```text
Modo mock
Modo real
```

---

## Modo mock

O modo mock serve para desenvolvimento e testes enquanto o token da Meta ainda não está configurado.

No arquivo `.env`, use:

```env
MOCK_INSTAGRAM=true
```

Nesse modo:

- o Cloudinary funciona de verdade;
- a imagem é enviada via API;
- a URL pública é gerada;
- o post entra na fila;
- o worker roda em background;
- a etapa do Instagram é simulada;
- nenhuma chamada real é feita ao Instagram.

Quando a simulação funciona, o status vira:

```text
mock_published
```

Esse modo não deve ser usado como prova final de publicação no Instagram. Ele serve apenas para validar o fluxo do sistema antes da configuração final da Meta.

---

## Modo real

O modo real deve ser usado na entrega final.

No arquivo `.env`, use:

```env
MOCK_INSTAGRAM=false
```

Também é necessário preencher:

```env
INSTAGRAM_USER_ID=seu_instagram_user_id
INSTAGRAM_ACCESS_TOKEN=seu_token_da_meta
```

Nesse modo:

- o Cloudinary continua enviando a imagem via API;
- o worker usa a URL pública gerada;
- a publicação é feita pela Instagram Graph API/Facebook Graph API;
- o post aparece de verdade no Instagram.

Quando a publicação real funciona, o status vira:

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
GRAPH_API_VERSION=v24.0
INSTAGRAM_USER_ID=seu_instagram_user_id
INSTAGRAM_ACCESS_TOKEN=seu_token_da_meta

# Modo de desenvolvimento
MOCK_INSTAGRAM=true

# Worker
QUEUE_FILE=data/posts_queue.json
WORKER_INTERVAL_SECONDS=15
```

Para a entrega final, alterar:

```env
MOCK_INSTAGRAM=false
```

---

## Como adicionar uma publicação na fila

Use o comando:

```bash
python scripts/enqueue_post.py "CAMINHO_DA_IMAGEM" "LEGENDA" "AAAA-MM-DDTHH:MM:SS"
```

Exemplo:

```bash
python scripts/enqueue_post.py "media/test.jpg" "Post publicado automaticamente via Claude Skill, Cloudinary API e Instagram Graph API." "2026-05-20T21:30:00"
```

O script vai:

```text
1. Localizar a imagem local.
2. Fazer upload para o Cloudinary.
3. Receber uma URL pública HTTPS.
4. Criar uma publicação com status pending.
5. Salvar a publicação no arquivo posts_queue.json.
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
python scripts/enqueue_post.py "media/test.jpg" "Teste em background com Cloudinary e modo mock." "2026-05-20T21:30:00"
```

### 5. Conferir o resultado

O worker deve processar a fila automaticamente.

O status deve mudar para:

```text
mock_published
```

---

## Como testar em modo real

### 1. Configurar o token da Meta

No `.env`:

```env
MOCK_INSTAGRAM=false
INSTAGRAM_USER_ID=seu_instagram_user_id
INSTAGRAM_ACCESS_TOKEN=seu_token_da_meta
```

### 2. Rodar o worker

```bash
python scripts/worker.py
```

### 3. Adicionar uma publicação

```bash
python scripts/enqueue_post.py "media/test.jpg" "Publicado automaticamente via API oficial." "2026-05-20T21:30:00"
```

### 4. Conferir resultado

O status esperado é:

```text
published
```

E o post deve aparecer no Instagram.

---

## Evidências para o desafio

Para demonstrar o funcionamento, registrar prints ou vídeo mostrando:

1. Estrutura do projeto.
2. Arquivo `SKILL.md`.
3. Código do upload para Cloudinary.
4. Código da integração com Instagram Graph API.
5. Upload da imagem para o Cloudinary.
6. URL pública `https://res.cloudinary.com/...`.
7. Fila com status `pending`.
8. Worker rodando em background.
9. Logs da execução.
10. Fila atualizada para `published`.
11. Post aparecendo no Instagram.

Durante o desenvolvimento, o status `mock_published` pode ser usado para demonstrar que a fila e o worker funcionam. Porém, para a entrega final, é necessário demonstrar a publicação real com status `published`.

---

## Requisitos atendidos

### Execução 100% via API

A publicação não utiliza navegador. Toda interação técnica é feita por API:

```text
Cloudinary API
Instagram Graph API / Facebook Graph API
```

---

### Publicação de conteúdo

O projeto foi estruturado para publicar uma foto com legenda no Instagram.

No modo real, o worker usa os endpoints oficiais da Graph API para criar o container de mídia e publicar o conteúdo.

---

### Execução em background

A execução autônoma é feita pelo arquivo:

```text
scripts/worker.py
```

O worker permanece ativo, verificando a fila e executando as publicações automaticamente.

---

### App Meta em sandbox/desenvolvimento

O projeto foi planejado para funcionar com um app Meta em modo desenvolvimento/sandbox, desde que o usuário tenha permissão no app e a conta Instagram esteja corretamente conectada à Página do Facebook.

---

### Sem automação de navegador

O projeto não usa:

```text
Selenium
Puppeteer
Playwright
Automação visual
Cliques simulados
Navegação automatizada
```

---

## Segurança

O arquivo `.env` contém credenciais sensíveis e não deve ser enviado para o GitHub.

O `.gitignore` deve conter:

```gitignore
.venv/
.env
__pycache__/
*.pyc
.DS_Store
```

---

## Limitações atuais

- A publicação real depende da obtenção de um token válido da Meta.
- A conta Instagram precisa ser profissional.
- A conta Instagram precisa estar conectada a uma Página do Facebook.
- A imagem precisa ter uma URL pública HTTPS.
- O modo mock não publica no Instagram real; ele serve apenas para desenvolvimento.

---

## Melhorias futuras

Possíveis melhorias para o projeto:

- Usar banco de dados em vez de JSON.
- Criar dashboard para visualizar fila e logs.
- Adicionar suporte a carrossel.
- Adicionar suporte a Reels.
- Criar sistema de retry automático.
- Criar logs estruturados em JSON.
- Publicar o worker em um servidor cloud.
- Implementar renovação ou validação automática de token.
- Adicionar testes automatizados.
- Criar interface simples para cadastro de publicações.

---

## Resumo técnico

A solução separa a responsabilidade da skill e da execução em background.

A Claude Skill organiza o fluxo e define as regras da automação. O Cloudinary resolve a necessidade de hospedar imagens locais em uma URL pública. A fila JSON armazena publicações pendentes. O worker Python executa em background e processa a fila automaticamente. No modo real, a publicação é enviada à Instagram Graph API/Facebook Graph API, sem uso de navegador ou automação visual.#   i n s t a g r a m - c l a u d e - s k i l l - p u b l i s h e r  
 