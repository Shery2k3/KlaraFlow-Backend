import boto3
from fastapi import UploadFile
from klaraflow.config.settings import settings
import uuid

class S3Service:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.AWS_S3_BUCKET_NAME

    async def upload_file(self, file: UploadFile, folder: str) -> str:
        file_extension = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_extension}"
        file_key = f"{folder}/{file_name}"

        self.s3.upload_fileobj(file.file,
                               self.bucket_name,
                               file_key,
                                ExtraArgs={"ContentType": file.content_type}
        )

        return f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"

s3_service = S3Service()