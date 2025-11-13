# Сводка изменений

## ✅ Выполнено

### 1. Удалена модель User
- Файл `/app/models/chat.py` - удалена класс `User`
- Файл `/app/models/__init__.py` - убран импорт `User`

### 2. Изменена модель Chat
- Поле `user_id` (Integer, ForeignKey) заменено на `external_id` (String)
- Удалена связь `relationship("User", back_populates="chats")`
- `external_id` теперь хранит ID пользователя из внешней системы напрямую

### 3. Обновлены схемы (Pydantic)
- `/app/schemas/chat.py` - `ChatResponse.user_id` заменён на `external_id`
- Удалён файл `/app/schemas/user.py`
- Обновлён `/app/schemas/__init__.py` - убраны импорты User схем

### 4. Обновлён API
- Файл `/app/api/chats.py` полностью переписан:
  - Удалена функция `get_current_user()`
  - Добавлена функция `get_external_id()` - получает `X-External-Id` из заголовка
  - Все эндпоинты теперь используют `external_id` вместо `current_user.id`
- Удалён файл `/app/api/users.py`

### 5. Обновлён main.py
- Убран импорт `from app.models import user`
- Убран импорт `from app.api.users import router as users_router`
- Удалён `app.include_router(users_router)`

### 6. База данных
- Таблица `users` удалена
- Таблица `chats` пересоздана с полем `external_id` (VARCHAR) вместо `user_id` (INTEGER)
- Таблица `chat_messages` осталась без изменений

### 7. Миграции
- Инициализирован Alembic (папка `/alembic/`, файл `alembic.ini`)
- Настроен `/alembic/env.py` для работы с моделями проекта
- Для создания таблиц используется скрипт `create_tables_migration.py`

## 📋 Структура таблиц

### chats
```sql
id              INTEGER PRIMARY KEY
external_id     VARCHAR(255) NOT NULL (индекс)
title           VARCHAR(500)
model           VARCHAR(200) NOT NULL
system_prompt   TEXT
created_at      TIMESTAMP WITH TIME ZONE
updated_at      TIMESTAMP WITH TIME ZONE
```

### chat_messages
```sql
id              INTEGER PRIMARY KEY
chat_id         INTEGER NOT NULL (FK -> chats.id, индекс)
role            VARCHAR(50) NOT NULL
content         TEXT NOT NULL
created_at      TIMESTAMP WITH TIME ZONE
```

## 🔧 Как использовать

### Создать чат
```bash
curl -X POST http://localhost:8000/chats/ \
  -H "Content-Type: application/json" \
  -H "X-External-Id: user123" \
  -d '{"title": "Мой чат", "model": "nvidia/nemotron-nano-12b-v2-vl:free"}'
```

### Отправить сообщение
```bash
curl -X POST http://localhost:8000/chats/message \
  -H "Content-Type: application/json" \
  -H "X-External-Id: user123" \
  -d '{"content": "Привет!", "chat_id": 1}'
```

### Получить список чатов
```bash
curl -X GET http://localhost:8000/chats/ \
  -H "X-External-Id: user123"
```

## 🚀 Запуск

```bash
# Запустить контейнеры
docker-compose up -d

# Создать таблицы
docker-compose exec api python create_tables_migration.py

# Проверить статус
curl http://localhost:8000/health
```

## 📝 Документация
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- API Usage Guide: `API_USAGE.md`

