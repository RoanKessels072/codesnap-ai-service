from fastapi import FastAPI
import logfire

from contextlib import asynccontextmanager
import uvicorn
from prometheus_client import make_asgi_app

from src.nats_client import NATSClient
from src.handlers import handle_get_feedback, handle_generate_rival, set_nats_client
from prometheus_fastapi_instrumentator import Instrumentator

nats_client = NATSClient()
logfire.configure()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting AI Service...")
    await nats_client.connect()
    
    set_nats_client(nats_client)
    
    await nats_client.subscribe("ai.feedback", handle_get_feedback)
    await nats_client.subscribe("ai.rival", handle_generate_rival)
    
    print("AI Service ready!")
    yield
    print("Shutting down AI Service...")
    await nats_client.close()

app = FastAPI(title="AI Service", lifespan=lifespan)
logfire.instrument_fastapi(app)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ai-service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)