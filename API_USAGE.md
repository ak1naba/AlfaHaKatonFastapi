# API Usage Guide

## Обзор

API для работы с чатами OpenRouter. Чаты привязаны к `external_id` пользователя из внешней системы.

## Авторизация

Все запросы к `/chats/*` требуют заголовок:
```
X-External-Id: <ваш_external_id>
```

## Endpoints

### 1. Создать новый чат
```bash
curl -X POST http://localhost:8000/chats/ \
  -H "Content-Type: application/json" \
  -H "X-External-Id: user123" \
  -d '{
    "title": "Мой первый чат",
    "model": "nvidia/nemotron-nano-12b-v2-vl:free",
    "system_prompt": "Ты полезный ассистент"
  }'
```

### 2. Получить список чатов
```bash
curl -X GET http://localhost:8000/chats/ \
  -H "X-External-Id: user123"
```

### 3. Получить чат по ID
```bash
curl -X GET http://localhost:8000/chats/1 \
  -H "X-External-Id: user123"
```

### 4. Обновить чат
```bash
curl -X PATCH http://localhost:8000/chats/1 \
  -H "Content-Type: application/json" \
  -H "X-External-Id: user123" \
  -d '{
    "title": "Обновлённое название"
  }'
```

### 5. Удалить чат
```bash
curl -X DELETE http://localhost:8000/chats/1 \
  -H "X-External-Id: user123"
```

### 6. Отправить сообщение в чат
```bash
# Отправка в существующий чат
curl -X POST http://localhost:8000/chats/message \
  -H "Content-Type: application/json" \
  -H "X-External-Id: user123" \
  -d '{
    "content": "Привет! Как дела?",
    "chat_id": 1
  }'

# Создание нового чата и отправка сообщения
curl -X POST http://localhost:8000/chats/message \
  -H "Content-Type: application/json" \
  -H "X-External-Id: user123" \
  -d '{
    "content": "Привет! Как дела?",
    "model": "nvidia/nemotron-nano-12b-v2-vl:free",
    "system_prompt": "Ты дружелюбный ассистент"
  }'
```

## Структура данных

### Chat
```json
{
  "id": 1,
  "external_id": "user123",
  "title": "Название чата",
  "model": "nvidia/nemotron-nano-12b-v2-vl:free",
  "system_prompt": "Системный промпт",
  "created_at": "2025-11-13T14:30:00Z",
  "updated_at": "2025-11-13T14:30:00Z",
  "messages": []
}
```

### ChatMessage
```json
{
  "id": 1,
  "chat_id": 1,
  "role": "user",
  "content": "Текст сообщения",
  "created_at": "2025-11-13T14:30:00Z"
}
```

## Запуск миграций

Для создания таблиц в базе данных:

```bash
# Вариант 1: Через скрипт
docker-compose exec api python create_tables_migration.py

# Вариант 2: Через Alembic (если настроен)
docker-compose exec api alembic upgrade head
```

## Доступные модели OpenRouter

- `nvidia/nemotron-nano-12b-v2-vl:free`
- `meta-llama/llama-3.2-3b-instruct:free`
- `google/gemini-flash-1.5:free`
- и другие (см. документацию OpenRouter)

## Переменные окружения

Создайте файл `.env`:
```env
OPENROUTER_API_KEY=your_api_key_here
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/openrouter_db
REDIS_URL=redis://cache:6379/0
```

