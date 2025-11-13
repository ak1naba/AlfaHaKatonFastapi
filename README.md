# 🚀 FastAPI Backend - OpenRouter + Google Calendar MCP

> **Микросервис для работы с OpenRouter API и Google Calendar через Model Context Protocol**

---

## 📋 Возможности проекта

### 🤖 OpenRouter Чаты
- ✅ Создание и управление чатами с AI моделями
- ✅ Привязка чатов к `external_id` пользователя
- ✅ История сообщений и контекст
- ✅ Поддержка различных моделей OpenRouter
- ✅ Изоляция данных между пользователями

### 📅 Google Calendar MCP
- ✅ **MCP Protocol** - стандартизированный интерфейс для AI
- ✅ **CRUD операции** с событиями календаря
- ✅ **AI Assistant** - естественноязыковые запросы
- ✅ **Умное планирование** встреч
- ✅ **OAuth 2.0** авторизация с Google
- ✅ Поиск свободного времени
- ✅ Работа с участниками и временными зонами

### 🔧 Технологии
- **FastAPI** - современный веб-фреймворк
- **PostgreSQL** - база данных
- **Redis** - кэширование
- **Docker** - контейнеризация
- **SQLAlchemy** - ORM
- **Alembic** - миграции

---

## 🚀 Быстрый старт

### 1. Запуск проекта

```bash
# Клонировать репозиторий
git clone <repository-url>
cd FastapiBackend

# Создать .env файл
cp .env.example .env
# Отредактируйте .env и добавьте OPENROUTER_API_KEY

# Запустить контейнеры
docker-compose up -d

# Создать таблицы
docker-compose exec api python create_tables_migration.py
```

### 2. Проверка

```bash
# Проверить статус
curl http://localhost:8000/health

# Swagger документация
open http://localhost:8000/docs
```

---

## 📡 API Endpoints

### Чаты OpenRouter

**Авторизация:** Все запросы требуют заголовок `X-External-Id`

```bash
# Создать чат
curl -X POST http://localhost:8000/chats/ \
  -H "X-External-Id: user123" \
  -H "Content-Type: application/json" \
  -d '{"title": "Мой чат"}'

# Отправить сообщение
curl -X POST http://localhost:8000/chats/message \
  -H "X-External-Id: user123" \
  -H "Content-Type: application/json" \
  -d '{"content": "Привет!", "chat_id": 1}'

# Получить список чатов
curl http://localhost:8000/chats/ \
  -H "X-External-Id: user123"
```

### Google Calendar

**Требуется:** `credentials.json` из Google Cloud Console

```bash
# Создать событие
curl -X POST http://localhost:8000/calendar/events \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Встреча",
    "start_time": "2025-11-14T10:00:00",
    "end_time": "2025-11-14T11:00:00"
  }'

# AI запрос (естественный язык)
curl -X POST http://localhost:8000/calendar/ai/natural-language \
  -H "Content-Type: application/json" \
  -d '{"request": "Создай встречу завтра в 10 утра"}'

# Найти свободное время
curl -X POST http://localhost:8000/calendar/find-free-time \
  -H "Content-Type: application/json" \
  -d '{"duration_minutes": 60, "date": "2025-11-14"}'
```

**Подробнее:** См. [docs/API_USAGE.md](docs/API_USAGE.md)

---

## 📅 Настройка Google Calendar

### Шаг 1: Получите credentials.json

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте проект
3. Включите "Google Calendar API"
4. Создайте OAuth 2.0 Client ID (Desktop app)
5. Скачайте JSON → переименуйте в `credentials.json`
6. Поместите в корень проекта

### Шаг 2: Первый запуск

```bash
# Установите зависимости
docker-compose exec api pip install -r requirements.txt

# Первый запрос откроет браузер для авторизации
curl http://localhost:8000/calendar/events
```

**Подробная инструкция:** [docs/GOOGLE_CALENDAR_MCP_GUIDE.md](docs/GOOGLE_CALENDAR_MCP_GUIDE.md)

---

## 📚 Документация

| Файл | Описание |
|------|----------|
| [docs/README_CALENDAR_MCP.md](docs/README_CALENDAR_MCP.md) | Полное руководство по Calendar MCP |
| [docs/GOOGLE_CALENDAR_MCP_GUIDE.md](docs/GOOGLE_CALENDAR_MCP_GUIDE.md) | Настройка Google Calendar API |
| [docs/API_USAGE.md](docs/API_USAGE.md) | Примеры использования API чатов |
| [Swagger UI](http://localhost:8000/docs) | Интерактивная документация API |
| [ReDoc](http://localhost:8000/redoc) | Альтернативная документация |

---

## 🏗️ Структура проекта

```
FastapiBackend/
├── app/
│   ├── api/                  # API endpoints
│   │   ├── chats.py         # OpenRouter чаты
│   │   └── calendar.py      # Google Calendar MCP
│   ├── mcp/                  # MCP серверы
│   │   └── google_calendar.py
│   ├── models/               # SQLAlchemy модели
│   │   └── chat.py
│   ├── schemas/              # Pydantic схемы
│   ├── services/             # Бизнес-логика
│   │   ├── chat_service.py
│   │   └── ai_calendar_service.py
│   ├── core/                 # Конфигурация
│   └── main.py               # Точка входа
├── docs/                     # Документация
│   ├── API_USAGE.md
│   ├── README_CALENDAR_MCP.md
│   └── GOOGLE_CALENDAR_MCP_GUIDE.md
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
└── .env
```

---

## 🔐 Переменные окружения

Создайте файл `.env`:

```env
# OpenRouter API
OPENROUTER_API_KEY=your_api_key_here

# Database
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/openrouter_db

# Redis
REDIS_URL=redis://cache:6379/0
```

---

## 🐛 Troubleshooting

### Проблема: API не запускается

```bash
# Проверьте логи
docker-compose logs api

# Пересоздайте контейнеры
docker-compose down && docker-compose up -d --build
```

### Проблема: credentials.json not found

```bash
# Убедитесь что файл в корне проекта
ls credentials.json

# Проверьте volume в docker-compose.yml
```

### Проблема: Token expired

```bash
# Удалите токен и авторизуйтесь заново
rm token.json
curl http://localhost:8000/calendar/events
```

---

## 🎯 Примеры использования

### 1. Создать чат-бота с календарём

```bash
# Создать чат
curl -X POST http://localhost:8000/chats/ \
  -H "X-External-Id: user123" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Календарный ассистент",
    "model": "nvidia/nemotron-nano-12b-v2-vl:free",
    "system_prompt": "Ты помогаешь управлять календарём Google Calendar"
  }'

# Спросить о свободном времени
curl -X POST http://localhost:8000/chats/message \
  -H "X-External-Id: user123" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Когда у меня свободное время на этой неделе?",
    "chat_id": 1
  }'
```

### 2. Умное планирование встречи

```bash
curl -X POST http://localhost:8000/calendar/ai/smart-schedule \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Презентация проекта",
    "duration_minutes": 90,
    "preferred_dates": ["2025-11-14", "2025-11-15", "2025-11-16"],
    "attendees": ["team@example.com"]
  }'
```

---

## 📈 Roadmap

- [ ] Recurring events (повторяющиеся события)
- [ ] Webhook notifications
- [ ] Групповое планирование
- [ ] Интеграция с Telegram/Slack
- [ ] Аналитика использования времени
- [ ] Rate limiting

---

## 🤝 Вклад в проект

Pull requests приветствуются! Пожалуйста:

1. Форкните репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

---

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.

---

## 📞 Поддержка

- **Документация:** См. файлы в корне проекта
- **Swagger UI:** http://localhost:8000/docs
- **Issues:** Создайте issue в GitHub

---

**Версия:** 1.0.0  
**Последнее обновление:** 13 ноября 2025

---

Made with ❤️ using FastAPI, Google Calendar API, and OpenRouter

