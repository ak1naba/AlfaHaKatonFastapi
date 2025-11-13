# OpenRouter Microservice

Микросервис для работы с OpenRouter API. Предоставляет функционал сохранения чатов и управления пользователями.

## Основные возможности

- Управление пользователями (создание, обновление, удаление)
- Создание и управление чатами
- Отправка сообщений в OpenRouter с сохранением истории
- Поддержка различных моделей OpenRouter

## API Endpoints

### Пользователи

#### POST /users/
Создание нового пользователя
```json
{
  "external_id": "user123",
  "token": "secret_token_12345"
}
```

#### GET /users/{external_id}
Получение пользователя по external_id

#### PATCH /users/{external_id}
Обновление токена или статуса пользователя
```json
{
  "token": "new_token",
  "is_active": true
}
```

#### DELETE /users/{external_id}
Удаление пользователя

#### GET /users/
Список всех пользователей

---

### Чаты

Все эндпоинты требуют заголовок `X-User-Token` для авторизации.

#### POST /chats/
Создание нового чата
```json
{
  "title": "Мой чат",
  "model": "nvidia/nemotron-nano-12b-v2-vl:free",
  "system_prompt": "Ты полезный ассистент"
}
```

#### GET /chats/
Список чатов текущего пользователя

#### GET /chats/{chat_id}
Получение чата по ID

#### PATCH /chats/{chat_id}
Обновление чата
```json
{
  "title": "Новое название",
  "system_prompt": "Новый промпт"
}
```

#### DELETE /chats/{chat_id}
Удаление чата

#### POST /chats/message
Отправка сообщения в чат
```json
{
  "content": "Привет! Как дела?",
  "chat_id": 1,
  "model": "nvidia/nemotron-nano-12b-v2-vl:free",
  "system_prompt": "Ты полезный ассистент"
}
```

Если `chat_id` не указан, создается новый чат.

Ответ:
```json
{
  "chat_id": 1,
  "user_message": {
    "id": 1,
    "chat_id": 1,
    "role": "user",
    "content": "Привет! Как дела?",
    "created_at": "2025-11-13T10:00:00Z"
  },
  "assistant_message": {
    "id": 2,
    "chat_id": 1,
    "role": "assistant",
    "content": "Привет! У меня всё отлично, спасибо! Чем могу помочь?",
    "created_at": "2025-11-13T10:00:01Z"
  }
}
```

#### GET /chats/{chat_id}/messages
Получение всех сообщений чата

---

## Использование

### 1. Создание пользователя

```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "user123",
    "token": "my_secret_token"
  }'
```

### 2. Отправка сообщения (создание нового чата)

```bash
curl -X POST "http://localhost:8000/chats/message" \
  -H "Content-Type: application/json" \
  -H "X-User-Token: my_secret_token" \
  -d '{
    "content": "Расскажи мне про Python",
    "model": "nvidia/nemotron-nano-12b-v2-vl:free"
  }'
```

### 3. Продолжение диалога в существующем чате

```bash
curl -X POST "http://localhost:8000/chats/message" \
  -H "Content-Type: application/json" \
  -H "X-User-Token: my_secret_token" \
  -d '{
    "content": "А что такое декораторы?",
    "chat_id": 1
  }'
```

### 4. Получение истории чата

```bash
curl -X GET "http://localhost:8000/chats/1/messages" \
  -H "X-User-Token: my_secret_token"
```

### 5. Список всех чатов

```bash
curl -X GET "http://localhost:8000/chats/" \
  -H "X-User-Token: my_secret_token"
```

---

## Структура базы данных

### Users
- `id` - автоинкремент
- `external_id` - ID из основной системы (уникальный)
- `token` - токен для авторизации
- `is_active` - активен ли пользователь
- `created_at` - дата создания
- `updated_at` - дата обновления

### Chats
- `id` - автоинкремент
- `user_id` - внешний ключ на users
- `title` - название чата
- `model` - модель OpenRouter
- `system_prompt` - системный промпт
- `created_at` - дата создания
- `updated_at` - дата обновления

### ChatMessages
- `id` - автоинкремент
- `chat_id` - внешний ключ на chats
- `role` - роль (user/assistant/system)
- `content` - содержимое сообщения
- `created_at` - дата создания

---

## Запуск

```bash
docker-compose up -d
```

API будет доступно по адресу: http://localhost:8000

Документация Swagger: http://localhost:8000/docs

---

## Переменные окружения

В файле `.env`:

```
OPENROUTER_API_KEY=your_openrouter_api_key
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/openrouter_db
REDIS_URL=redis://cache:6379/0
```

