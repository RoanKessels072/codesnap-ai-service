
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str = "ai-service"
    port: int = 8005
    
    nats_url: str = "nats://localhost:4222"
    
    google_api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()