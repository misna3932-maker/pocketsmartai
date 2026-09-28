import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

class Settings:
    app_name: str = os.getenv("APP_NAME", "PocketSmart AI")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    gemini_api_url: str = os.getenv(
        "GEMINI_API_URL",
        "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    )
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "5"))
    database_path: Path = ROOT / os.getenv("DATABASE_PATH", "instance/pocketsmart.db")
    upload_dir: Path = ROOT / "instance" / "uploads"

settings = Settings()
settings.database_path.parent.mkdir(parents=True, exist_ok=True)
settings.upload_dir.mkdir(parents=True, exist_ok=True)
