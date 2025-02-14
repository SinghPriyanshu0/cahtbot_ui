from decouple import config
import os

class Settings:
    GENAI_API_KEY: str = os.getenv("GENAI_API_KEY", config("GENAI_API_KEY", default=""))

settings = Settings()

