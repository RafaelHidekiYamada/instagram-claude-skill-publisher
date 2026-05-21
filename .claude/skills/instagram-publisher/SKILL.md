---
name: instagram-publisher
description: Use esta skill quando o usuário quiser agendar ou publicar fotos no Instagram usando uma imagem local enviada ao Cloudinary via API e depois publicada pela Instagram Graph API/Facebook Graph API, sem automação de navegador.
---

# Skill de Publicação no Instagram

Esta skill agenda e publica fotos no Instagram usando automação baseada em APIs.

## Regras principais

- Nunca usar automação via navegador.
- Nunca usar Selenium, Puppeteer, Playwright, cliques simulados ou automação visual.
- Toda publicação no Instagram deve acontecer pela Instagram Graph API/Facebook Graph API.
- Imagens locais devem ser enviadas ao Cloudinary via API antes de serem usadas no Instagram.
- A URL `secure_url` retornada pelo Cloudinary deve ser usada como `image_url` na publicação do Instagram.
- O script `worker.py` é responsável pela execução em background.
- A fila de publicações fica no arquivo `data/posts_queue.json`.

## Arquivos do projeto

- Cliente de upload para Cloudinary: `scripts/cloudinary_client.py`
- Cliente da Instagram Graph API: `scripts/instagram_client.py`
- Script para adicionar publicação na fila: `scripts/enqueue_post.py`
- Worker em background: `scripts/worker.py`
- Fila de publicações: `data/posts_queue.json`
- Arquivo de logs: `logs/publisher.log`

## Fluxo de funcionamento

Quando o usuário pedir para agendar ou publicar uma foto no Instagram:

1. Identificar o caminho local da imagem.
2. Identificar a legenda da publicação.
3. Identificar a data e horário de agendamento.
4. Enviar a imagem local para o Cloudinary usando API.
5. Salvar a URL pública `secure_url` no arquivo `data/posts_queue.json`.
6. Garantir que o worker em background esteja rodando.
7. O worker verifica automaticamente a fila e publica os posts pendentes quando chega o horário agendado.

## Comando para adicionar uma publicação na fila

```bash
python scripts/enqueue_post.py "CAMINHO_DA_IMAGEM" "LEGENDA" "AAAA-MM-DDTHH:MM:SS"