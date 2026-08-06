import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Sanjeevani (AERO) Hospital Management Engine"
    API_V1_STR: str = "/api/v1"
    
    # JWT Auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", "sanjeevani_secret_key_super_secure_992182741")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Storage
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_BUCKET: str = os.getenv("SUPABASE_BUCKET", "hospital-documents")
    LOCAL_UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

settings = Settings()

os.makedirs(settings.LOCAL_UPLOAD_DIR, exist_ok=True)
