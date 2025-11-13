from fastapi import FastAPI
from app.core.database import engine, Base
from app.models import chat  # импортируем модели
from app.api.chats import router as chats_router

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OpenRouter Microservice",
    description="Микросервис для работы с OpenRouter API",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(chats_router)

@app.get("/")
async def root():
    return {"message": "API is working"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/routes")
async def get_all_routes():
    """Показывает все доступные маршруты"""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, "name", "Unknown")
            })
    return {"routes": routes}

@app.get("/routes-debug")
async def get_all_routes():
    """Показывает все доступные маршруты"""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, "name", "Unknown")
            })
    return {"routes": routes}