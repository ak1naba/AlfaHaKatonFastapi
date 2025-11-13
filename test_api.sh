#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"

echo -e "${BLUE}=== Тестирование OpenRouter Microservice ===${NC}\n"

# 1. Проверка здоровья API
echo -e "${GREEN}1. Проверка здоровья API${NC}"
curl -s "$BASE_URL/health" | jq .
echo -e "\n"

# 2. Создание пользователя
echo -e "${GREEN}2. Создание пользователя${NC}"
USER_RESPONSE=$(curl -s -X POST "$BASE_URL/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "test_user_'$(date +%s)'",
    "token": "test_token_'$(date +%s)'"
  }')
echo $USER_RESPONSE | jq .

# Извлекаем токен
USER_TOKEN=$(echo $USER_RESPONSE | jq -r '.token')
EXTERNAL_ID=$(echo $USER_RESPONSE | jq -r '.external_id')

echo -e "\n${BLUE}Токен пользователя: $USER_TOKEN${NC}\n"

# 3. Отправка первого сообщения (создание чата)
echo -e "${GREEN}3. Отправка первого сообщения (создание нового чата)${NC}"
FIRST_MSG_RESPONSE=$(curl -s -X POST "$BASE_URL/chats/message" \
  -H "Content-Type: application/json" \
  -H "X-User-Token: $USER_TOKEN" \
  -d '{
    "content": "Привет! Расскажи кратко про Python",
    "model": "nvidia/nemotron-nano-12b-v2-vl:free"
  }')
echo $FIRST_MSG_RESPONSE | jq .

# Извлекаем chat_id
CHAT_ID=$(echo $FIRST_MSG_RESPONSE | jq -r '.chat_id')
echo -e "\n${BLUE}ID чата: $CHAT_ID${NC}\n"

# 4. Продолжение диалога
echo -e "${GREEN}4. Продолжение диалога в существующем чате${NC}"
curl -s -X POST "$BASE_URL/chats/message" \
  -H "Content-Type: application/json" \
  -H "X-User-Token: $USER_TOKEN" \
  -d '{
    "content": "А что такое декораторы?",
    "chat_id": '"$CHAT_ID"'
  }' | jq .
echo -e "\n"

# 5. Получение списка чатов
echo -e "${GREEN}5. Получение списка чатов пользователя${NC}"
curl -s -X GET "$BASE_URL/chats/" \
  -H "X-User-Token: $USER_TOKEN" | jq .
echo -e "\n"

# 6. Получение истории сообщений
echo -e "${GREEN}6. Получение истории сообщений чата${NC}"
curl -s -X GET "$BASE_URL/chats/$CHAT_ID/messages" \
  -H "X-User-Token: $USER_TOKEN" | jq .
echo -e "\n"

# 7. Обновление чата
echo -e "${GREEN}7. Обновление названия чата${NC}"
curl -s -X PATCH "$BASE_URL/chats/$CHAT_ID" \
  -H "Content-Type: application/json" \
  -H "X-User-Token: $USER_TOKEN" \
  -d '{
    "title": "Беседа про Python"
  }' | jq .
echo -e "\n"

# 8. Получение информации о пользователе
echo -e "${GREEN}8. Получение информации о пользователе${NC}"
curl -s -X GET "$BASE_URL/users/$EXTERNAL_ID" | jq .
echo -e "\n"

# 9. Список всех маршрутов
echo -e "${GREEN}9. Список всех доступных маршрутов${NC}"
curl -s "$BASE_URL/routes" | jq '.routes[] | select(.path | startswith("/users") or startswith("/chats"))'
echo -e "\n"

echo -e "${BLUE}=== Тестирование завершено ===${NC}"
echo -e "${BLUE}Создан пользователь: $EXTERNAL_ID${NC}"
echo -e "${BLUE}Создан чат: $CHAT_ID${NC}"

