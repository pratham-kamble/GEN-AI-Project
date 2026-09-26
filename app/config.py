from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"
    embedding_model: str = "all-MiniLM-L6-v2"


settings = Settings()