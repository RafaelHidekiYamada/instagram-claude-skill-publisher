import os
from pathlib import Path
from datetime import datetime

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv


load_dotenv()


class CloudinaryClient:
    def __init__(self):
        self.cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        self.api_key = os.getenv("CLOUDINARY_API_KEY")
        self.api_secret = os.getenv("CLOUDINARY_API_SECRET")

        if not self.cloud_name:
            raise ValueError("CLOUDINARY_CLOUD_NAME não configurado no arquivo .env")

        if not self.api_key:
            raise ValueError("CLOUDINARY_API_KEY não configurado no arquivo .env")

        if not self.api_secret:
            raise ValueError("CLOUDINARY_API_SECRET não configurado no arquivo .env")

        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True
        )

    def upload_image(self, image_path: str) -> dict:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

        if not path.is_file():
            raise ValueError(f"O caminho informado não é um arquivo: {image_path}")

        allowed_extensions = [".jpg", ".jpeg", ".png", ".webp"]

        if path.suffix.lower() not in allowed_extensions:
            raise ValueError(
                f"Formato não recomendado: {path.suffix}. "
                f"Use uma imagem JPG, JPEG, PNG ou WEBP."
            )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        public_id = f"post_{timestamp}_{path.stem}"

        result = cloudinary.uploader.upload(
            str(path),
            folder="instagram_skill",
            public_id=public_id,
            resource_type="image",
            overwrite=False
        )

        secure_url = result.get("secure_url")
        returned_public_id = result.get("public_id")

        if not secure_url:
            raise Exception(f"Upload feito, mas sem secure_url na resposta: {result}")

        return {
            "secure_url": secure_url,
            "public_id": returned_public_id,
            "format": result.get("format"),
            "width": result.get("width"),
            "height": result.get("height"),
            "bytes": result.get("bytes")
        }