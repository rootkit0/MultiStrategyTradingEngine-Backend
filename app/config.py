import os
from dotenv import load_dotenv

# Load variables from .env into process environment
load_dotenv()

class Settings:
    @property
    def DATABASE_URL(self) -> str:
        return os.getenv(
            "DATABASE_URL",
            "mysql+pymysql://user:password@your-host:3306/trading",  # fallback (optional)
        )

    @property
    def OLLAMA_API_URL(self) -> str:
        return os.getenv(
            "OLLAMA_API_URL",
            "https://ollama.xavierberga.com/api",
        )

settings = Settings()