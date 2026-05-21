import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

from instagram_client import InstagramClient


load_dotenv()

QUEUE_FILE = os.getenv("QUEUE_FILE", "data/posts_queue.json")
WORKER_INTERVAL_SECONDS = int(os.getenv("WORKER_INTERVAL_SECONDS", "15"))
LOG_FILE = "logs/publisher.log"


def log(message: str):
    os.makedirs("logs", exist_ok=True)

    timestamp = datetime.now().isoformat(timespec="seconds")
    line = f"[{timestamp}] {message}"

    print(line)

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(line + "\n")


def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []

    with open(QUEUE_FILE, "r", encoding="utf-8") as file:
        content = file.read().strip()

        if not content:
            return []

        return json.loads(content)


def save_queue(queue):
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)

    with open(QUEUE_FILE, "w", encoding="utf-8") as file:
        json.dump(queue, file, indent=2, ensure_ascii=False)


def should_publish(post):
    if post.get("status") != "pending":
        return False

    scheduled_at = datetime.fromisoformat(post["scheduled_at"])
    now = datetime.now()

    return scheduled_at <= now


def process_queue():
    queue = load_queue()
    client = InstagramClient()
    changed = False

    for post in queue:
        if not should_publish(post):
            continue

        post_id = post["id"]

        try:
            log(f"Iniciando publicação do post {post_id}")
            log(f"Imagem pública usada: {post['image_url']}")

            result = client.publish_photo(
                image_url=post["image_url"],
                caption=post["caption"]
            )

            is_mock = result.get("mock", False)

            if is_mock:
                post["status"] = "mock_published"
                log(f"Post {post_id} simulado com sucesso em modo MOCK.")
                log("Nenhuma chamada real foi feita ao Instagram.")
            else:
                post["status"] = "published"
                log(f"Post {post_id} publicado com sucesso no Instagram.")

            post["published_at"] = datetime.now().isoformat(timespec="seconds")
            post["creation_id"] = result["creation_id"]
            post["media_id"] = result["media_id"]
            post["error"] = None

            changed = True

            log(f"media_id={result['media_id']}")

        except Exception as error:
            post["status"] = "failed"
            post["error"] = str(error)
            changed = True

            log(f"Erro ao publicar post {post_id}: {error}")

    if changed:
        save_queue(queue)


def main():
    log("Worker iniciado em background.")
    log(f"Verificando fila a cada {WORKER_INTERVAL_SECONDS} segundos.")

    while True:
        process_queue()
        time.sleep(WORKER_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()