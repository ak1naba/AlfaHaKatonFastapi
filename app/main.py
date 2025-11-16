from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.models import chat  # импортируем модели
from app.api.chats import router as chats_router

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OpenRouter Microservice",
    description="Микросервис для работы с OpenRouter API и Google Calendar через MCP",
    version="1.0.0"
)

# CORS для всех доменов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chats_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
