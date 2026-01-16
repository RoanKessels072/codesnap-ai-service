
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str = "ai-service"
    port: int = 8005
    logfire_token: str | None = None
    logfire_service_name: str | None = None
    
    nats_url: str = "nats://localhost:4222"
    
    google_api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()