# 🗓️ Google Calendar MCP для FastAPI Backend
> **Model Context Protocol (MCP)** интеграция с Google Calendar + AI Assistant
## 📋 Содержание
- [Обзор](#обзор)
- [Быстрый старт](#быстрый-старт)
- [Архитектура](#архитектура)
- [API Endpoints](#api-endpoints)
- [Примеры использования](#примеры-использования)
- [Документация](#документация)
---
## 🎯 Обзор
Этот проект предоставляет **полнофункциональную интеграцию Google Calendar** через **Model Context Protocol (MCP)** с поддержкой AI-assisted планирования через OpenRouter.
### Ключевые возможности
✅ **MCP Сервер** - стандартизированный интерфейс для AI моделей  
✅ **REST API** - 10+ endpoints для работы с календарём  
✅ **AI Assistant** - естественноязыковые запросы и умное планирование  
✅ **Google Calendar** - полная интеграция (OAuth 2.0, события, участники)  
✅ **OpenRouter Integration** - работа с чат-ботами  
### Что такое MCP?
**Model Context Protocol** - это открытый протокол для предоставления контекста AI-моделям. MCP позволяет AI:
- Получать доступ к внешним данным и сервисам
- Выполнять действия от имени пользователя
- Использовать стандартизированный интерфейс "tools"
---
## 🚀 Быстрый старт
### 1. Получите Google Calendar credentials
```
https://console.cloud.google.com
→ Create Project
→ Enable "Google Calendar API"
→ Create Credentials → OAuth 2.0 Client ID → Desktop app
→ Download JSON → Rename to credentials.json
→ Place in project root
```
### 2. Установите зависимости
```bash
# Обновите requirements.txt уже включает все нужные пакеты
docker-compose exec api pip install -r requirements.txt
# Или пересоберите контейнер
docker-compose up -d --build api
```
### 3. Сделайте первый запрос
```bash
curl http://localhost:8000/calendar/events
```
При первом запросе откроется браузер для авторизации в Google.
### 4. Готово! 🎉
```bash
# Создайте событие
curl -X POST http://localhost:8000/calendar/events \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Моя первая встреча через MCP",
    "start_time": "2025-11-14T10:00:00",
    "end_time": "2025-11-14T11:00:00"
  }'
```
---
## 🏗️ Архитектура
```
┌─────────────────────────────────────────────────┐
│              FastAPI Application                 │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐      ┌──────────────────┐    │
│  │   REST API   │      │  AI Assistant    │    │
│  │ /calendar/*  │◄────►│ Natural Language │    │
│  └──────┬───────┘      └────────┬─────────┘    │
│         │                        │               │
│         └────────┬───────────────┘               │
│                  │                                │
│         ┌────────▼─────────┐                     │
│         │   MCP Server     │                     │
│         │  5 Tools:        │                     │
│         │  - list_events   │                     │
│         │  - create_event  │                     │
│         │  - update_event  │                     │
│         │  - delete_event  │                     │
│         │  - find_free     │                     │
│         └────────┬─────────┘                     │
│                  │                                │
└──────────────────┼────────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │  Google Calendar    │
        │   OAuth 2.0 API     │
        └─────────────────────┘
```
### Компоненты
**1. MCP Server** (`app/mcp/google_calendar.py`)
- Аутентификация OAuth 2.0
- 5 MCP инструментов для работы с календарём
- Автоматическое обновление токенов
**2. REST API** (`app/api/calendar.py`)
- 8 базовых endpoints (CRUD)
- 2 AI-powered endpoints
- Pydantic валидация
**3. AI Assistant** (`app/services/ai_calendar_service.py`)
- Обработка естественного языка
- Интеграция с OpenRouter
- Умное планирование встреч
---
## 📡 API Endpoints
### Базовые операции
```
GET    /calendar/tools              - Список MCP инструментов
POST   /calendar/tools/execute      - Выполнить MCP инструмент
POST   /calendar/events             - Создать событие
GET    /calendar/events             - Получить список событий
PATCH  /calendar/events/{id}        - Обновить событие
DELETE /calendar/events/{id}        - Удалить событие
POST   /calendar/find-free-time     - Найти свободное время
GET    /calendar/health             - Health check
```
### AI-Powered операции
```
POST   /calendar/ai/natural-language    - Естественноязыковые запросы
POST   /calendar/ai/smart-schedule      - Умное планирование встреч
```
---
## 💡 Примеры использования
### 1. Создать событие (REST API)
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
### 2. Естественноязыковой запрос (AI)
```bash
curl -X POST http://localhost:8000/calendar/ai/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Создай встречу с менеджером завтра в 14:00 на час"
  }'
```
### 3. Умное планирование
```bash
curl -X POST http://localhost:8000/calendar/ai/smart-schedule \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Презентация инвестору",
    "duration_minutes": 90,
    "preferred_dates": ["2025-11-14", "2025-11-15", "2025-11-16"],
    "attendees": ["investor@example.com"]
  }'
```
### 4. Найти свободное время
```bash
curl -X POST http://localhost:8000/calendar/find-free-time \
  -H "Content-Type: application/json" \
  -d '{
    "duration_minutes": 60,
    "date": "2025-11-14"
  }'
```
### 5. Выполнить MCP инструмент напрямую
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
### 6. Интеграция с чатами
```bash
# 1. Создать чат с календарным ассистентом
curl -X POST http://localhost:8000/chats/ \
  -H "X-External-Id: user123" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Мой календарный помощник",
    "model": "nvidia/nemotron-nano-12b-v2-vl:free",
    "system_prompt": "Ты помогаешь мне управлять календарём Google Calendar"
  }'
# 2. Задать вопрос о календаре
curl -X POST http://localhost:8000/chats/message \
  -H "X-External-Id: user123" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Когда у меня свободное время на следующей неделе?",
    "chat_id": 1
  }'
```
---
## 📚 Документация
### Файлы документации
1. **CALENDAR_QUICK_START.md** - Быстрый старт (3 шага)
2. **GOOGLE_CALENDAR_MCP_GUIDE.md** - Полное руководство по настройке
3. **AI_CALENDAR_EXAMPLES.md** - Примеры кода (Python/JS)
4. **CALENDAR_MCP_COMPLETE.md** - Сводка по установке
5. **MCP_CALENDAR_FINAL_SUMMARY.md** - Итоговая сводка
6. **CHANGELOG_MCP.md** - История изменений
### Онлайн документация
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **MCP Tools:** http://localhost:8000/calendar/tools
- **Health Check:** http://localhost:8000/calendar/health
---
## 🔐 Безопасность
### Файлы credentials
⚠️ **Важно:** Никогда не публикуйте эти файлы!
```
credentials.json    # OAuth credentials от Google (добавлен в .gitignore)
token.json         # Access и refresh токены (добавлен в .gitignore)
```
### Production deployment
Для production рекомендуется использовать:
- **Service Accounts** вместо OAuth 2.0
- **Environment variables** для хранения секретов
- **HTTPS** для всех запросов
- **Rate limiting** для защиты от злоупотреблений
---
## 🛠️ Структура файлов
```
FastapiBackend/
├── app/
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── google_calendar.py           # MCP сервер
│   ├── api/
│   │   └── calendar.py                  # REST API endpoints
│   ├── services/
│   │   └── ai_calendar_service.py       # AI Assistant
│   └── main.py                          # calendar_router добавлен
│
├── credentials.json.example             # Пример credentials
├── credentials.json                     # ← Ваш файл (не в git)
├── token.json                           # ← Генерируется авто (не в git)
│
├── CALENDAR_QUICK_START.md
├── GOOGLE_CALENDAR_MCP_GUIDE.md
├── AI_CALENDAR_EXAMPLES.md
├── CALENDAR_MCP_COMPLETE.md
├── MCP_CALENDAR_FINAL_SUMMARY.md
├── CHANGELOG_MCP.md
└── README_CALENDAR_MCP.md               # ← Этот файл
```
---
## 🐛 Troubleshooting
### Ошибка: "credentials.json not found"
```bash
# Скачайте credentials.json из Google Cloud Console
# Поместите в корень проекта (где docker-compose.yml)
```
### Ошибка: "Token expired or revoked"
```bash
# Удалите старый токен
rm token.json
# При следующем запросе откроется браузер для авторизации
curl http://localhost:8000/calendar/events
```
### Ошибка: "Calendar API has not been used"
```bash
# Включите Google Calendar API в Google Cloud Console:
# APIs & Services → Library → Google Calendar API → Enable
```
### Docker контейнер не видит credentials.json
```bash
# Убедитесь что файл в правильном месте
ls credentials.json
# Проверьте volume в docker-compose.yml
# Должно быть: volumes: - .:/app
```
---
## 📈 Roadmap
- [ ] Поддержка recurring events (повторяющиеся события)
- [ ] Webhook notifications для real-time обновлений
- [ ] Групповое планирование с учётом занятости участников
- [ ] Интеграция с Telegram/Slack для уведомлений
- [ ] Аналитика использования времени
- [ ] Автоматические умные напоминания
- [ ] Service Account для production
- [ ] Rate limiting и кэширование
---
## 🤝 Интеграция с другими сервисами
### OpenRouter Chats
Календарь полностью интегрирован с чат-ботами OpenRouter
### Zapier/Make
MCP инструменты можно использовать для автоматизации
### Telegram/Slack (планируется)
Уведомления о событиях и быстрое создание встреч
---
## 📞 Поддержка
- **Документация:** См. файлы *_GUIDE.md
- **API Docs:** http://localhost:8000/docs
- **Examples:** AI_CALENDAR_EXAMPLES.md
---
## ✅ Статус
🟢 **Google Calendar MCP полностью реализован и готов к использованию!**
**Версия:** 1.0.0  
**Дата:** 13 ноября 2025  
**Автор:** AI Assistant
---
**Следующий шаг:** Получите `credentials.json` из Google Cloud Console и начните использовать! 🚀
