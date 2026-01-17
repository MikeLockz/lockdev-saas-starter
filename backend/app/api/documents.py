import uuid

from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.models.user import User
from app.services.storage import storage_service

router = APIRouter()


@router.post("/upload-url")
async def get_upload_url(filename: str, current_user: User = Depends(get_current_user)):
    object_name = f"users/{current_user.id}/{uuid.uuid4()}-{filename}"
    url_data = storage_service.generate_presigned_url(object_name)
    return {"url_data": url_data, "object_name": object_name}
