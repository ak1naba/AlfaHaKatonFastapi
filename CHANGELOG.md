# Описание изменений проекта

## Что было сделано

Проект переработан из сервиса генерации персон в микросервис-прослойку для работы с OpenRouter API.

### Новые модели базы данных:

1. **User** (`app/models/user.py`)
   - Хранит пользователей из основной системы
   - Поля: id, external_id (уникальный ID из основной системы), token (для авторизации), is_active

2. **Chat** (`app/models/chat.py`)
   - Хранит чаты пользователей
   - Поля: id, user_id, title, model, system_prompt
   - Связь: один пользователь -> много чатов

3. **ChatMessage** (`app/models/chat.py`)
   - Хранит сообщения в чатах
   - Поля: id, chat_id, role (user/assistant/system), content
   - Связь: один чат -> много сообщений

### Новые API эндпоинты:

#### Управление пользователями (`/users`)
- `POST /users/` - создание пользователя
- `GET /users/{external_id}` - получение пользователя
- `PATCH /users/{external_id}` - обновление токена/статуса
- `DELETE /users/{external_id}` - удаление пользователя
- `GET /users/` - список всех пользователей

#### Работа с чатами (`/chats`)
Все эндпоинты требуют заголовок `X-User-Token` для авторизации.

- `POST /chats/` - создание чата
- `GET /chats/` - список чатов пользователя
- `GET /chats/{chat_id}` - получение чата
- `PATCH /chats/{chat_id}` - обновление чата
- `DELETE /chats/{chat_id}` - удаление чата
- `POST /chats/message` - отправка сообщения (главный эндпоинт!)
- `GET /chats/{chat_id}/messages` - получение истории сообщений

### Новые сервисы:

- **chat_service.py** - взаимодействие с OpenRouter API

### Схемы Pydantic:

- **user.py** - UserCreate, UserResponse, UserUpdate
- **chat.py** - ChatCreate, ChatResponse, ChatUpdate, SendMessageRequest, SendMessageResponse

### Обновления:

- Обновлен `pydantic` до версии 2.x
- Обновлен `config.py` для использования `pydantic-settings`
- Обновлены все схемы для использования `ConfigDict(from_attributes=True)`

### Старый функционал:

Старые эндпоинты генерации персон (`/persons`) оставлены для обратной совместимости, но могут быть удалены.

## Как использовать

### 1. Создать .env файл
```bash
cp .env.example .env
# Отредактировать .env и добавить OPENROUTER_API_KEY
```

### 2. Запустить через Docker
```bash
docker-compose up -d
```

### 3. Создать пользователя
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"external_id": "user123", "token": "my_token"}'
```

### 4. Отправить сообщение в новый чат
```bash
curl -X POST "http://localhost:8000/chats/message" \
  -H "Content-Type: application/json" \
  -H "X-User-Token: my_token" \
  -d '{"content": "Привет! Как дела?"}'
```

### 5. Продолжить диалог
```bash
curl -X POST "http://localhost:8000/chats/message" \
  -H "Content-Type: application/json" \
  -H "X-User-Token: my_token" \
  -d '{"content": "Расскажи подробнее", "chat_id": 1}'
```

## Архитектура

```
User (основная система)
    ↓ external_id + token
    ↓
Микросервис (FastAPI)
    ↓ OPENROUTER_API_KEY
    ↓
OpenRouter API
```

## Преимущества

1. **Централизованное хранение** - вся история чатов в одной БД
2. **Простая авторизация** - по токену в заголовке
3. **Контекст диалога** - автоматически сохраняется и передается
4. **Изоляция** - каждый пользователь видит только свои чаты
5. **Масштабируемость** - готово к работе как микросервис

## Следующие шаги (опционально)

- [ ] Добавить пагинацию для списка сообщений
- [ ] Добавить лимиты на количество сообщений
- [ ] Добавить кэширование через Redis
- [ ] Добавить метрики и логирование
- [ ] Добавить rate limiting
- [ ] Удалить старый функционал генерации персон

