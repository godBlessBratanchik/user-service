import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db
from .kafka import kafka_producer, KAFKA_ENABLED
from .consumers import start_consumers
from .api_profiles import router as profiles_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 50)
    print("Starting Profile Service...")
    print("=" * 50)

    await init_db()
    print("✓ Database initialized")

    if KAFKA_ENABLED:
        await kafka_producer.start()
        await start_consumers()
    else:
        print("⊘ Kafka disabled")

    print("=" * 50)
    print("✓ Profile Service is ready!")
    print("=" * 50)

    yield

    print("Stopping Profile Service...")
    if KAFKA_ENABLED:
        await kafka_producer.stop()
    print("✓ Profile Service stopped")

app = FastAPI(
    title="Profile Service",
    description="Микросервис управления профилями пользователей",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles_router)

@app.get("/", tags=["health"])
async def root():
    return {
        "service": "profile-service",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "database": "connected",
        "kafka": "connected" if KAFKA_ENABLED else "disabled"
    }
