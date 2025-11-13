"""
Примеры использования API микросервиса OpenRouter
"""

import requests

BASE_URL = "http://localhost:8000"

# 1. Создание пользователя
def create_user():
    response = requests.post(
        f"{BASE_URL}/users/",
        json={
            "external_id": "user_from_main_system_123",
            "token": "secret_token_abc123"
        }
    )
    print("Created user:", response.json())
    return response.json()

# 2. Получение пользователя
def get_user(external_id):
    response = requests.get(f"{BASE_URL}/users/{external_id}")
    print("User info:", response.json())
    return response.json()

# 3. Создание нового чата и отправка первого сообщения
def send_first_message(token):
    response = requests.post(
        f"{BASE_URL}/chats/message",
        headers={"X-User-Token": token},
        json={
            "content": "Привет! Расскажи мне про Python",
            "model": "nvidia/nemotron-nano-12b-v2-vl:free",
            "system_prompt": "Ты опытный программист Python"
        }
    )
    print("First message response:", response.json())
    return response.json()

# 4. Продолжение диалога
def continue_chat(token, chat_id):
    response = requests.post(
        f"{BASE_URL}/chats/message",
        headers={"X-User-Token": token},
        json={
            "content": "А что такое декораторы?",
            "chat_id": chat_id
        }
    )
    print("Continue chat response:", response.json())
    return response.json()

# 5. Получение списка чатов
def get_chats(token):
    response = requests.get(
        f"{BASE_URL}/chats/",
        headers={"X-User-Token": token}
    )
    print("User chats:", response.json())
    return response.json()

# 6. Получение истории сообщений чата
def get_chat_history(token, chat_id):
    response = requests.get(
        f"{BASE_URL}/chats/{chat_id}/messages",
        headers={"X-User-Token": token}
    )
    print("Chat history:", response.json())
    return response.json()

# 7. Создание чата вручную
def create_chat(token):
    response = requests.post(
        f"{BASE_URL}/chats/",
        headers={"X-User-Token": token},
        json={
            "title": "Чат про программирование",
            "model": "nvidia/nemotron-nano-12b-v2-vl:free",
            "system_prompt": "Ты полезный ассистент по программированию"
        }
    )
    print("Created chat:", response.json())
    return response.json()

# 8. Обновление чата
def update_chat(token, chat_id):
    response = requests.patch(
        f"{BASE_URL}/chats/{chat_id}",
        headers={"X-User-Token": token},
        json={
            "title": "Обновленное название чата",
            "system_prompt": "Новый системный промпт"
        }
    )
    print("Updated chat:", response.json())
    return response.json()

# 9. Удаление чата
def delete_chat(token, chat_id):
    response = requests.delete(
        f"{BASE_URL}/chats/{chat_id}",
        headers={"X-User-Token": token}
    )
    print("Delete response:", response.json())
    return response.json()

# 10. Обновление пользователя
def update_user(external_id):
    response = requests.patch(
        f"{BASE_URL}/users/{external_id}",
        json={
            "token": "new_secret_token_xyz789",
            "is_active": True
        }
    )
    print("Updated user:", response.json())
    return response.json()


if __name__ == "__main__":
    # Пример полного сценария
    print("=== Создание пользователя ===")
    user = create_user()
    token = user["token"]
    external_id = user["external_id"]
    
    print("\n=== Отправка первого сообщения ===")
    first_msg = send_first_message(token)
    chat_id = first_msg["chat_id"]
    
    print("\n=== Продолжение диалога ===")
    continue_chat(token, chat_id)
    
    print("\n=== Получение истории чата ===")
    get_chat_history(token, chat_id)
    
    print("\n=== Получение списка всех чатов ===")
    get_chats(token)
    
    print("\n=== Создание нового чата вручную ===")
    new_chat = create_chat(token)
    
    print("\n=== Получение информации о пользователе ===")
    get_user(external_id)

