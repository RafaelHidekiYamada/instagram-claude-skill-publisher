import os
import uuid
import requests
from dotenv import load_dotenv


load_dotenv()


class InstagramClient:
    def __init__(self):
        self.graph_api_version = os.getenv("GRAPH_API_VERSION", "v24.0")
        self.instagram_user_id = os.getenv("INSTAGRAM_USER_ID")
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.mock_instagram = os.getenv("MOCK_INSTAGRAM", "false").lower() == "true"

        self.base_url = f"https://graph.facebook.com/{self.graph_api_version}"

        if self.mock_instagram:
            print("MOCK_INSTAGRAM=true: o Instagram real não será chamado.")
            return

        if not self.instagram_user_id:
            raise ValueError("INSTAGRAM_USER_ID não configurado no .env")

        if not self.access_token:
            raise ValueError("INSTAGRAM_ACCESS_TOKEN não configurado no .env")

    def create_media_container(self, image_url: str, caption: str) -> str:
        if self.mock_instagram:
            return f"mock_creation_{uuid.uuid4()}"

        url = f"{self.base_url}/{self.instagram_user_id}/media"

        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }

        response = requests.post(url, data=payload, timeout=30)
        data = response.json()

        if response.status_code >= 400:
            raise Exception(f"Erro ao criar container no Instagram: {data}")

        creation_id = data.get("id")

        if not creation_id:
            raise Exception(f"Resposta sem creation_id: {data}")

        return creation_id

    def publish_media(self, creation_id: str) -> str:
        if self.mock_instagram:
            return f"mock_media_{uuid.uuid4()}"

        url = f"{self.base_url}/{self.instagram_user_id}/media_publish"

        payload = {
            "creation_id": creation_id,
            "access_token": self.access_token
        }

        response = requests.post(url, data=payload, timeout=30)
        data = response.json()

        if response.status_code >= 400:
            raise Exception(f"Erro ao publicar mídia no Instagram: {data}")

        media_id = data.get("id")

        if not media_id:
            raise Exception(f"Resposta sem media_id: {data}")

        return media_id

    def publish_photo(self, image_url: str, caption: str) -> dict:
        creation_id = self.create_media_container(image_url, caption)
        media_id = self.publish_media(creation_id)

        return {
            "creation_id": creation_id,
            "media_id": media_id,
            "mock": self.mock_instagram
        }