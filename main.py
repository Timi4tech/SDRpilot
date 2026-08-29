import os

from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import sys
import uvicorn


from src.infrastructure.web.middleware import setup_middleware
from src.infrastructure.web.Routers.routers import register_routers
from src.infrastructure.database.mongo_client import client, verify_connection
from src.infrastructure.config.redis_config import redis_service

TESTING = os.getenv("ENV") == "test"

logging.basicConfig(
    level=logging.INFO,   
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    stream=sys.stdout,     
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await verify_connection()   
    redis_service.connect()  
    await redis_service.verify_connection()
    yield
    

    if not TESTING:
        mongo_client.close()
        await redis_service.close()

app = FastAPI(lifespan=lifespan)

setup_middleware(app)
register_routers(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)