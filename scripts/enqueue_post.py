import json
import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

from cloudinary_client import CloudinaryClient


load_dotenv()

QUEUE_FILE = os.getenv("QUEUE_FILE", "data/posts_queue.json")


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


def enqueue_post(local_image_path: str, caption: str, scheduled_at: str):
    print("Iniciando upload da imagem para o Cloudinary...")

    cloudinary_client = CloudinaryClient()
    upload_result = cloudinary_client.upload_image(local_image_path)

    image_url = upload_result["secure_url"]
    cloudinary_public_id = upload_result["public_id"]

    print("Upload concluído com sucesso.")
    print(f"URL pública gerada: {image_url}")

    queue = load_queue()

    post = {
        "id": str(uuid.uuid4()),
        "local_image_path": local_image_path,
        "image_url": image_url,
        "caption": caption,
        "scheduled_at": scheduled_at,
        "status": "pending",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "published_at": None,
        "cloudinary_public_id": cloudinary_public_id,
        "cloudinary_format": upload_result.get("format"),
        "cloudinary_width": upload_result.get("width"),
        "cloudinary_height": upload_result.get("height"),
        "cloudinary_bytes": upload_result.get("bytes"),
        "creation_id": None,
        "media_id": None,
        "error": None
    }

    queue.append(post)
    save_queue(queue)

    print("Post adicionado à fila com sucesso.")
    print(json.dumps(post, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso:")
        print('python scripts/enqueue_post.py "LOCAL_IMAGE_PATH" "CAPTION" "YYYY-MM-DDTHH:MM:SS"')
        print("")
        print("Exemplo:")
        print('python scripts/enqueue_post.py "media/test.jpg" "Legenda teste" "2026-05-20T15:30:00"')
        sys.exit(1)

    local_image_path_arg = sys.argv[1]
    caption_arg = sys.argv[2]
    scheduled_at_arg = sys.argv[3]

    enqueue_post(local_image_path_arg, caption_arg, scheduled_at_arg)