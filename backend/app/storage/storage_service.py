import os
import uuid
import httpx
from fastapi import UploadFile
from app.core.config import settings

class StorageService:
    @staticmethod
    async def upload_file(file: UploadFile, subfolder: str = "documents") -> str:
        """
        Uploads a file to Supabase Storage if configured; otherwise stores locally
        and returns the accessible URL.
        """
        file_ext = os.path.splitext(file.filename)[1] or ".bin"
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        contents = await file.read()

        # Try Supabase Storage if credentials are configured
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                target_url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_BUCKET}/{subfolder}/{unique_filename}"
                headers = {
                    "Authorization": f"Bearer {settings.SUPABASE_KEY}",
                    "apikey": settings.SUPABASE_KEY,
                    "Content-Type": file.content_type or "application/octet-stream"
                }
                async with httpx.AsyncClient() as client:
                    resp = await client.post(target_url, content=contents, headers=headers)
                    if resp.status_code in (200, 201):
                        public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET}/{subfolder}/{unique_filename}"
                        return public_url
            except Exception as e:
                print(f"Supabase upload attempt failed, using local storage fallback: {e}")

        # Local storage fallback
        sub_dir = os.path.join(settings.LOCAL_UPLOAD_DIR, subfolder)
        os.makedirs(sub_dir, exist_ok=True)
        local_path = os.path.join(sub_dir, unique_filename)
        
        with open(local_path, "wb") as f:
            f.write(contents)

        return f"/uploads/{subfolder}/{unique_filename}"

storage_service = StorageService()
