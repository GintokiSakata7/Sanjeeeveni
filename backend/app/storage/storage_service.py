import os
import uuid
from fastapi import UploadFile
from app.core.config import settings


class StorageService:
    @staticmethod
    async def upload_file(file: UploadFile, subfolder: str = "documents") -> str:
        """
        Uploads a file to Supabase Storage using the official Python SDK.
        On success returns the public CDN URL.
        Falls back to local /uploads directory if Supabase is not configured or upload fails.

        Bucket layout:  hospital-documents/verification_docs/<uuid>.<ext>
        """
        file_ext = os.path.splitext(file.filename or "file")[1] or ".bin"
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        object_path = f"{subfolder}/{unique_filename}"
        contents = await file.read()
        content_type = file.content_type or "application/octet-stream"

        # ── Supabase Storage Upload via SDK ─────────────────────────────────────
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                from supabase import create_client, Client
                supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

                response = supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
                    path=object_path,
                    file=contents,
                    file_options={"content-type": content_type, "upsert": "true"},
                )

                # SDK returns an object with .path on success
                public_url = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(object_path)
                print(f"[Storage] ✅ Uploaded to Supabase: {public_url}")
                return public_url

            except Exception as e:
                print(f"[Storage] ⚠️ Supabase upload failed: {e} — using local fallback.")

        # ── Local Storage Fallback ───────────────────────────────────────────────
        sub_dir = os.path.join(settings.LOCAL_UPLOAD_DIR, subfolder)
        os.makedirs(sub_dir, exist_ok=True)
        local_path = os.path.join(sub_dir, unique_filename)

        with open(local_path, "wb") as f:
            f.write(contents)

        local_url = f"/uploads/{subfolder}/{unique_filename}"
        print(f"[Storage] 📁 Saved locally: {local_url}")
        return local_url


storage_service = StorageService()
