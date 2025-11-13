# Google Calendar MCP - Руководство по настройке

## 📋 Что такое MCP?

**MCP (Model Context Protocol)** - это открытый протокол для предоставления контекста AI-моделям. В данном проекте MCP используется для интеграции Google Calendar с языковыми моделями.

## 🚀 Настройка Google Calendar API

### Шаг 1: Создание проекта в Google Cloud Console

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Перейдите в раздел "APIs & Services" → "Library"
4. Найдите и включите "Google Calendar API"

### Шаг 2: Создание OAuth 2.0 credentials

1. Перейдите в "APIs & Services" → "Credentials"
2. Нажмите "Create Credentials" → "OAuth client ID"
3. Выберите тип приложения: "Desktop app"
4. Дайте имя приложению (например, "FastAPI Calendar MCP")
5. Нажмите "Create"
6. Скачайте JSON файл с credentials
7. Переименуйте файл в `credentials.json` и поместите в корень проекта

### Шаг 3: Первый запуск

При первом запуске API:
1. MCP откроет браузер для авторизации
2. Войдите в Google аккаунт
3. Разрешите доступ к календарю
4. Токены сохранятся в файл `token.json`

**⚠️ Важно:** 
- Файл `credentials.json` содержит секретные данные - не публикуйте его!
- Добавьте в `.gitignore`:
  ```
  credentials.json
  token.json
  ```

## 📦 Установка зависимостей

```bash
# В контейнере
docker-compose exec api pip install -r requirements.txt

# Или локально
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## 🔧 API Endpoints

### 1. Получить список доступных MCP инструментов

```bash
curl http://localhost:8000/calendar/tools
```

Ответ содержит все доступные инструменты с описанием параметров.

### 2. Создать событие

```bash
curl -X POST http://localhost:8000/calendar/events \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Встреча с командой",
    "description": "Обсуждение проекта",
    "start_time": "2025-11-14T10:00:00",
    "end_time": "2025-11-14T11:00:00",
    "timezone": "Europe/Moscow",
    "attendees": ["team@example.com"]
  }'
```

### 3. Получить список событий

```bash
# Все предстоящие события
curl http://localhost:8000/calendar/events

# С параметрами
curl "http://localhost:8000/calendar/events?max_results=20&calendar_id=primary"
```

### 4. Обновить событие

```bash
curl -X PATCH http://localhost:8000/calendar/events/EVENT_ID \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "event123",
    "summary": "Новое название встречи",
    "start_time": "2025-11-14T11:00:00"
  }'
```

### 5. Удалить событие

```bash
curl -X DELETE http://localhost:8000/calendar/events/EVENT_ID
```

### 6. Найти свободное время

```bash
curl -X POST http://localhost:8000/calendar/find-free-time \
  -H "Content-Type: application/json" \
  -d '{
    "duration_minutes": 60,
    "date": "2025-11-14"
  }'
```

### 7. Выполнить MCP инструмент напрямую

```bash
curl -X POST http://localhost:8000/calendar/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "list_events",
    "arguments": {
      "calendar_id": "primary",
      "max_results": 5
    }
  }'
```

## 🤖 Интеграция с AI моделями

MCP предоставляет стандартизированный интерфейс для AI моделей:

```python
from app.mcp.google_calendar import GoogleCalendarMCP

# Инициализация
calendar = GoogleCalendarMCP()

# Получить список доступных инструментов
tools = calendar.get_tools()

# AI модель может выбрать и выполнить инструмент
result = calendar.execute_tool("create_event", {
    "summary": "AI-созданная встреча",
    "start_time": "2025-11-15T14:00:00",
    "end_time": "2025-11-15T15:00:00"
})
```

## 📊 Примеры использования

### Создание встречи на завтра в 10:00

```python
from datetime import datetime, timedelta

tomorrow = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0)
end_time = tomorrow + timedelta(hours=1)

result = calendar.create_event(
    summary="Важная встреча",
    start_time=tomorrow.isoformat(),
    end_time=end_time.isoformat(),
    timezone="Europe/Moscow"
)
```

### Найти свободное время на неделе

```python
from datetime import datetime, timedelta

for i in range(7):
    date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
    result = calendar.find_free_time(
        duration_minutes=30,
        date=date
    )
    print(f"{date}: {result['count']} свободных слотов")
```

## 🔐 Безопасность

1. **Не публикуйте credentials.json** - содержит секретные ключи
2. **token.json** - содержит access и refresh токены пользователя
3. Рекомендуется использовать **service accounts** для production
4. Ограничьте scope до минимально необходимого

## 🐛 Troubleshooting

### Ошибка: "credentials.json not found"
```bash
# Убедитесь что файл находится в корне проекта
ls credentials.json

# Если работаете в Docker, проверьте volume
docker-compose exec api ls /app/credentials.json
```

### Ошибка: "Token has been expired or revoked"
```bash
# Удалите старый токен и авторизуйтесь заново
rm token.json
# При следующем запросе откроется браузер для авторизации
```

### Ошибка: "Calendar API has not been used in project"
1. Перейдите в Google Cloud Console
2. Включите Calendar API для вашего проекта
3. Подождите несколько минут

## 📚 Документация

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- MCP Tools: http://localhost:8000/calendar/tools
- Health Check: http://localhost:8000/calendar/health

## 🎯 Roadmap

- [ ] Поддержка recurring events (повторяющиеся события)
- [ ] Интеграция с OpenRouter для AI-assisted scheduling
- [ ] Webhook notifications для событий
- [ ] Поддержка нескольких календарей
- [ ] Конфликтное разрешение времени
- [ ] Автоматические напоминания

