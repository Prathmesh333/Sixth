from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SIXTH_", env_file=".env", extra="ignore")
    data_dir: Path = Path("data")
    database_url: str = ""
    demo_access_code: str = ""
    google_client_id: str = ""
    whatsapp_enabled: bool = False
    whatsapp_send_enabled: bool = False
    whatsapp_app_secret: str = ""
    whatsapp_identity_secret: str = ""
    whatsapp_allowed_numbers: list[str] = []
    whatsapp_verify_token: str = ""
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_business_number: str = ""
    whatsapp_api_version: str = ""
    whatsapp_encryption_key: str = ""
    public_url: str = "http://127.0.0.1:5173"
    memory_backend: Literal["sqlite_fixture", "falkordb"] = "sqlite_fixture"
    falkordb_host: str = "127.0.0.1"
    falkordb_port: int = 6379
    falkordb_username: str | None = None
    falkordb_password: str | None = None
    falkordb_ssl: bool = False
    model_base_url: str = "https://api.openai.com/v1"
    model_api_key: str = ""
    model_name: str = ""
    demo_login: bool = False
    cookie_secure: bool = False
    allowed_origins: list[str] = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://testserver",
    ]
