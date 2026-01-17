import boto3

from app.core.config import settings


class StorageService:
    def __init__(self):
        try:
            self.s3 = boto3.client("s3", region_name=settings.AWS_REGION)
            self.bucket = "lockdev-app-storage"  # Should be from settings
            self.available = True
        except Exception:
            self.s3 = None
            self.available = False

    def generate_presigned_url(self, object_name: str, expiration=3600):
        if not self.available:
            return "mock-url"
        try:
            response = self.s3.generate_presigned_post(
                self.bucket, object_name, ExpiresIn=expiration
            )
            return response
        except Exception:
            return None


storage_service = StorageService()
