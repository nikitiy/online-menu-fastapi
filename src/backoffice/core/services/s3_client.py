import io
import os
import uuid
from datetime import datetime, timedelta, timezone

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException, UploadFile
from PIL import Image

from src.backoffice.core.config import s3_settings


class S3Client:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=s3_settings.endpoint_url,
            aws_access_key_id=s3_settings.access_key,
            aws_secret_access_key=s3_settings.secret_key,
            region_name=s3_settings.region,
            use_ssl=s3_settings.use_https,
        )
        self.bucket_name = s3_settings.bucket_name

    async def upload_file(
        self,
        file: UploadFile,
        folder: str = "menu-images",
        generate_thumbnails: bool = True,
    ) -> dict:
        try:
            await self._validate_file(file)

            file_extension = self._get_file_extension(file.filename)
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = f"{folder}/{unique_filename}"

            file_content = await file.read()

            upload_result = await self._upload_to_s3(
                file_path, file_content, file.content_type
            )

            result = {
                "filename": unique_filename,
                "original_filename": file.filename,
                "file_path": file_path,
                "file_size": len(file_content),
                "mime_type": file.content_type,
                "url": upload_result["url"],
                "thumbnails": [],
            }

            if generate_thumbnails and self._is_image_file(file.content_type):
                thumbnails = await self._generate_thumbnails(
                    file_content, folder, unique_filename, file_extension
                )
                result["thumbnails"] = thumbnails

                try:
                    with Image.open(file.file) as img:
                        result["width"] = img.width
                        result["height"] = img.height
                except (OSError, IOError, ValueError):
                    pass

            return result

        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Error uploading file: {str(e)}"
            )

    async def delete_file(self, file_path: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError as e:
            print(f"Error deleting file {file_path}: {e}")
            return False

    async def get_presigned_url(self, file_path: str, expiry_hours: int = 1) -> str:
        try:
            expiry = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_path},
                ExpiresIn=int(
                    expiry.timestamp() - datetime.now(timezone.utc).timestamp()
                ),
            )
            return url
        except ClientError as e:
            raise HTTPException(
                status_code=400, detail=f"Error generating URL: {str(e)}"
            )

    async def file_exists(self, file_path: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError:
            return False

    async def _validate_file(self, file: UploadFile):
        if not file.filename:
            raise HTTPException(status_code=400, detail="File name not specified")

        if hasattr(file, "size") and file.size > s3_settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"The file size exceeds the maximum allowed ({s3_settings.max_file_size} byte)",
            )

        file_extension = self._get_file_extension(file.filename).lower()
        if file_extension not in s3_settings.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension. Allowed: {', '.join(s3_settings.allowed_extensions)}",
            )

        if file.content_type not in s3_settings.allowed_mime_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(s3_settings.allowed_mime_types)}",
            )

    @staticmethod
    def _get_file_extension(filename: str) -> str:
        return os.path.splitext(filename)[1]

    @staticmethod
    def _is_image_file(content_type: str) -> bool:
        return content_type.startswith("image/")

    async def _upload_to_s3(
        self, file_path: str, file_content: bytes, content_type: str
    ) -> dict:
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=file_content,
                ContentType=content_type,
                ACL="public-read",
            )

            url = f"{s3_settings.endpoint_url}/{self.bucket_name}/{file_path}"

            return {"url": url, "file_path": file_path}
        except NoCredentialsError:
            raise HTTPException(status_code=500, detail="S3 authentication error")
        except ClientError as e:
            raise HTTPException(
                status_code=500, detail=f"Error uploading to S3: {str(e)}"
            )

    async def _generate_thumbnails(
        self, file_content: bytes, folder: str, base_filename: str, file_extension: str
    ) -> list:
        if not s3_settings.generate_thumbnails:
            return []

        thumbnails = []

        try:
            with Image.open(io.BytesIO(file_content)) as img:
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")

                for size_name, (width, height) in [
                    ("small", s3_settings.thumbnail_sizes[0]),
                    ("medium", s3_settings.thumbnail_sizes[1]),
                    ("large", s3_settings.thumbnail_sizes[2]),
                ]:
                    thumbnail = img.copy()
                    thumbnail.thumbnail((width, height), Image.Resampling.LANCZOS)

                    thumbnail_buffer = io.BytesIO()
                    thumbnail.save(thumbnail_buffer, format="JPEG", quality=85)
                    thumbnail_buffer.seek(0)

                    thumbnail_filename = f"{os.path.splitext(base_filename)[0]}_{size_name}{file_extension}"
                    thumbnail_path = f"{folder}/thumbnails/{thumbnail_filename}"

                    self.s3_client.put_object(
                        Bucket=self.bucket_name,
                        Key=thumbnail_path,
                        Body=thumbnail_buffer.getvalue(),
                        ContentType="image/jpeg",
                        ACL="public-read",
                    )

                    thumbnails.append(
                        {
                            "size": size_name,
                            "width": thumbnail.width,
                            "height": thumbnail.height,
                            "file_path": thumbnail_path,
                            "url": f"{s3_settings.endpoint_url}/{self.bucket_name}/{thumbnail_path}",
                        }
                    )

        except Exception as e:
            print(f"Error generating thumbnails: {e}")

        return thumbnails


s3_client = S3Client()
