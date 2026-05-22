# Relatório do Desafio — Instagram Claude Skill Publisher

## 1. Objetivo

O objetivo deste projeto foi criar uma skill para o Claude capaz de organizar e executar um fluxo automatizado de publicação de fotos no Instagram usando APIs oficiais.

A solução foi desenvolvida para atender aos seguintes requisitos do desafio:

- Execução 100% via API.
- Publicação de pelo menos uma foto com legenda no Instagram.
- Execução em background.
- Uso de app Meta em modo desenvolvimento/sandbox.
- Demonstração do funcionamento com prints e evidências.
- Proibição de automação via navegador, Selenium, Puppeteer, Playwright ou cliques simulados.

O projeto foi construído com uma arquitetura simples, funcional e testável, separando a skill do Claude, o upload da imagem, a fila de publicação e o worker responsável pela execução em background.

---

## 2. Ferramenta escolhida

A ferramenta escolhida foi **Claude Code Skills**.

A escolha foi feita porque esse formato permite estruturar uma skill com instruções próprias, regras de execução, scripts auxiliares e um fluxo claro de automação.

A skill criada está localizada em:

```text
.claude/skills/instagram-publisher/SKILL.md
```

Ela define as regras de funcionamento do projeto, incluindo:

- Não usar automação de navegador.
- Não usar Selenium, Puppeteer ou Playwright.
- Usar Cloudinary para transformar uma imagem local em URL pública.
- Usar Instagram Graph API/Facebook Graph API para publicação.
- Usar um worker Python para execução em background.

---

## 3. Arquitetura da solução

A arquitetura foi dividida em camadas:

```text
Claude Skill
↓
Script de enfileiramento
↓
Cloudinary API
↓
Fila local em JSON
↓
Worker Python em background
↓
Instagram Graph API / Facebook Graph API
↓
Post publicado no Instagram
```

A skill do Claude é responsável por organizar o fluxo e definir as regras da automação. O Cloudinary é utilizado para hospedar a imagem local e gerar uma URL pública HTTPS. A fila JSON armazena as publicações pendentes. O worker Python roda em background, monitora a fila e executa a publicação automaticamente quando chega o horário configurado.

---

## 4. Justificativa do uso do Cloudinary

A Instagram Graph API não recebe diretamente arquivos locais, como:

```text
media/test.jpg
```

Ela precisa receber uma URL pública HTTPS da imagem.

Por isso, antes da publicação, o projeto envia a imagem local para o Cloudinary via API. O Cloudinary retorna uma URL pública, chamada `secure_url`, que é usada como `image_url` na chamada para a Instagram Graph API.

Fluxo do upload:

```text
Imagem local
↓
Cloudinary API
↓
URL pública HTTPS
↓
Instagram Graph API
```

Exemplo do tipo de URL gerada:

```text
https://res.cloudinary.com/...
```

Esse fluxo permite que a publicação continue sendo feita 100% via API, sem depender de upload manual ou navegador.

---

## 5. Justificativa do uso de worker em background

O desafio exigia que a skill funcionasse de forma autônoma, sem intervenção manual durante a execução.

Por isso, foi criado um worker Python responsável por rodar em background.

O arquivo responsável por essa execução é:

```text
scripts/worker.py
```

O worker executa as seguintes etapas:

```text
1. Lê o arquivo data/posts_queue.json.
2. Procura publicações com status pending.
3. Verifica se o horário scheduled_at já chegou.
4. Publica a imagem usando a Instagram Graph API.
5. Atualiza o status da publicação.
6. Registra logs da execução.
```

Com isso, a skill não precisa ficar responsável por permanecer ativa o tempo todo. Ela organiza o fluxo, enquanto o worker executa a tarefa automaticamente.

---

## 6. Estrutura do projeto

A estrutura principal do projeto ficou organizada da seguinte forma:

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

## 7. Arquivos principais

### 7.1 Skill do Claude

Arquivo:

```text
.claude/skills/instagram-publisher/SKILL.md
```

Responsável por definir as instruções da skill.

A skill contém regras como:

```text
- Nunca usar automação via navegador.
- Nunca usar Selenium, Puppeteer, Playwright ou cliques simulados.
- Toda publicação deve acontecer pela Instagram Graph API/Facebook Graph API.
- A imagem local deve ser enviada ao Cloudinary via API.
- O worker em background é responsável pela execução automática.
```

---

### 7.2 Cliente Cloudinary

Arquivo:

```text
scripts/cloudinary_client.py
```

Responsável por fazer upload da imagem local para o Cloudinary.

O script valida o caminho da imagem, envia o arquivo por API e retorna dados como:

```text
secure_url
public_id
format
width
height
bytes
```

A informação mais importante para o Instagram é a `secure_url`, pois ela é a URL pública HTTPS usada no momento da publicação.

---

### 7.3 Script de enfileiramento

Arquivo:

```text
scripts/enqueue_post.py
```

Responsável por criar uma nova tarefa de publicação.

Ele recebe:

```text
1. Caminho local da imagem.
2. Legenda.
3. Data e horário de agendamento.
```

Depois executa:

```text
1. Upload da imagem para o Cloudinary.
2. Recebimento da URL pública.
3. Criação do objeto da publicação.
4. Salvamento no arquivo data/posts_queue.json.
```

Exemplo de comando:

```bash
python scripts/enqueue_post.py "media/test.jpg" "Publicado automaticamente via Claude Skill, Cloudinary API e Instagram Graph API." "2026-05-22T15:30:00"
```

---

### 7.4 Fila de publicações

Arquivo:

```text
data/posts_queue.json
```

Esse arquivo funciona como uma fila local simples.

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
  "creation_id": null,
  "media_id": null,
  "error": null
}
```

Principais status utilizados:

```text
pending          → publicação aguardando execução
mock_published   → publicação simulada em modo de desenvolvimento
published        → publicação real concluída no Instagram
failed           → erro durante a execução
```

---

### 7.5 Worker em background

Arquivo:

```text
scripts/worker.py
```

Responsável por executar a automação em background.

Comando para rodar:

```bash
python scripts/worker.py
```

O worker permanece ativo verificando a fila a cada intervalo definido no `.env`:

```env
WORKER_INTERVAL_SECONDS=15
```

Quando encontra uma publicação pendente cujo horário já chegou, ele chama o cliente do Instagram e executa a publicação.

---

### 7.6 Cliente Instagram

Arquivo:

```text
scripts/instagram_client.py
```

Responsável por se comunicar com a Instagram Graph API/Facebook Graph API.

No modo real, o fluxo utiliza dois endpoints principais:

```text
POST /{ig-user-id}/media
POST /{ig-user-id}/media_publish
```

Primeiro o sistema cria um container de mídia com a imagem e a legenda. Depois publica esse container no Instagram.

---

## 8. Modos de execução

O projeto possui dois modos de execução:

```text
Modo mock
Modo real
```

---

### 8.1 Modo mock

O modo mock foi usado durante o desenvolvimento, enquanto o token da Meta ainda não estava configurado.

No arquivo `.env`, o modo mock é ativado com:

```env
MOCK_INSTAGRAM=true
```

Nesse modo:

- A imagem é enviada de verdade para o Cloudinary.
- A URL pública HTTPS é gerada de verdade.
- O post entra de verdade na fila JSON.
- O worker roda de verdade em background.
- A etapa final do Instagram é simulada.
- Nenhuma chamada real é feita para publicar no Instagram.

Quando o modo mock funciona, o status da fila muda para:

```text
mock_published
```

Esse modo foi útil para validar a estrutura do sistema antes da integração final com a Meta.

---

### 8.2 Modo real

O modo real foi usado para a publicação final no Instagram.

No arquivo `.env`, o modo real é ativado com:

```env
MOCK_INSTAGRAM=false
```

Também foram configuradas as variáveis:

```env
GRAPH_API_VERSION=v25.0
INSTAGRAM_USER_ID=ID_DA_CONTA_INSTAGRAM
INSTAGRAM_ACCESS_TOKEN=TOKEN_DA_META
```

Nesse modo:

- A imagem é enviada para o Cloudinary via API.
- A URL pública é salva na fila.
- O worker roda em background.
- O worker chama a Instagram Graph API/Facebook Graph API.
- O post é publicado de verdade no Instagram.

Quando a publicação real funciona, o status da fila muda para:

```text
published
```

---

## 9. Configuração de ambiente

As dependências do projeto estão no arquivo:

```text
requirements.txt
```

Conteúdo:

```txt
requests
python-dotenv
cloudinary
```

Instalação:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 10. Variáveis de ambiente

O projeto usa um arquivo `.env` para armazenar credenciais e configurações.

Exemplo de configuração:

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

O arquivo `.env` não deve ser enviado ao GitHub, pois contém credenciais sensíveis.

Por isso, o projeto possui um `.gitignore` com:

```gitignore
.venv/
.env
__pycache__/
*.pyc
*.pyo
*.pyd
logs/*.log
data/posts_queue.json
```

---

## 11. Execução em background

O worker pode ser executado diretamente no terminal:

```bash
python scripts/worker.py
```

Também pode ser iniciado em outra janela do PowerShell no Windows:

```powershell
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\.venv\Scripts\activate; python scripts\worker.py"
```

Esse comando permite que o worker continue rodando como um processo separado, monitorando a fila automaticamente.

---

## 12. Fluxo da publicação real

O fluxo completo da publicação real foi:

```text
1. Imagem local salva em media/test.jpg.
2. Script enqueue_post.py executado.
3. Imagem enviada para o Cloudinary via API.
4. Cloudinary retornou uma URL pública HTTPS.
5. Publicação foi adicionada ao posts_queue.json com status pending.
6. Worker.py rodou em background.
7. Worker identificou a publicação pendente.
8. Worker chamou a Instagram Graph API.
9. Instagram Graph API criou o container de mídia.
10. Instagram Graph API publicou o container.
11. Fila foi atualizada para status published.
12. Post apareceu na conta Instagram configurada.
```

---

## 13. Evidências coletadas

As evidências foram organizadas na pasta:

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

## 14. Requisitos atendidos

| Requisito | Status |
|---|---|
| Skill estruturada no Claude Code | Concluído |
| Execução via API | Concluído |
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

## 15. Evidência final de publicação real

Após configurar o `INSTAGRAM_USER_ID`, o `INSTAGRAM_ACCESS_TOKEN` e alterar `MOCK_INSTAGRAM=false`, o worker processou uma publicação real usando a Instagram Graph API/Facebook Graph API.

O sistema realizou o upload da imagem local para o Cloudinary, salvou a URL pública na fila e executou a publicação automaticamente pelo worker em background.

O status da publicação foi atualizado para:

```text
published
```

E o post apareceu na conta Instagram configurada com a legenda definida no momento do enfileiramento.

---

## 16. Segurança

O projeto foi estruturado para evitar exposição de credenciais.

O arquivo `.env` não foi enviado ao GitHub.

As credenciais sensíveis ficam apenas localmente:

```text
CLOUDINARY_API_SECRET
INSTAGRAM_ACCESS_TOKEN
INSTAGRAM_USER_ID
```

O repositório contém apenas o arquivo `.env.example`, que mostra o formato esperado das variáveis sem expor dados reais.

---

## 17. Limitações

Algumas limitações atuais do projeto:

- A fila usa JSON local, adequada para demonstração e MVP.
- O worker roda localmente, dependendo da máquina estar ligada.
- O token da Meta pode expirar, dependendo do tipo de token utilizado.
- O projeto publica foto única, não carrossel ou reels.
- Não há interface visual; o fluxo é feito por comandos e pela skill.

---

## 18. Melhorias futuras

Possíveis evoluções:

- Substituir JSON por banco de dados.
- Criar painel visual para gerenciar publicações.
- Adicionar suporte a carrossel.
- Adicionar suporte a reels.
- Criar sistema de retry automático.
- Implementar logs estruturados em JSON.
- Hospedar o worker em um servidor cloud.
- Criar validação automática do token.
- Adicionar testes automatizados.
- Criar endpoint HTTP para receber tarefas de publicação.
- Adicionar renovação ou alerta de expiração do token.

---

## 19. Conclusão

O projeto atendeu ao objetivo do desafio ao implementar uma skill para Claude integrada a um fluxo automatizado de publicação no Instagram.

A solução usa APIs oficiais, não depende de automação de navegador, possui um worker em background e realizou uma publicação real no Instagram com legenda.

A arquitetura separa responsabilidades de forma clara:

```text
Skill do Claude → orquestração
Cloudinary → hospedagem pública da imagem
JSON → fila local
Worker Python → execução em background
Instagram Graph API → publicação real
```

Com isso, o projeto demonstra capacidade de integração com APIs, organização de arquitetura, execução autônoma e documentação técnica para entrega.