import os
from typing import List, Dict, Any
from openai import OpenAI
from app.core.config import settings
from app.services.message_parser import parse_ai_response, ParsedMessage

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
)


def load_system_prompt() -> str:
    """    
    Returns:
        Содержимое промпта или пустая строка если файл не найден
    """
    prompt_path = os.path.join(os.path.dirname(__file__), '..', '..', 'prompt.md')
    
    if os.path.exists(prompt_path):
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Failed to load system prompt from {prompt_path}: {e}")
            return ""
    
    return ""


async def send_chat_message(
    messages: List[Dict[str, str]],
    model: str = "deepseek/deepseek-chat-v3.1:free",
    system_prompt: str = None
) -> str:
    """
    Отправляет сообщения в OpenRouter и возвращает ответ
    
    Args:
        messages: Список сообщений в формате [{"role": "user", "content": "text"}]
        model: Модель для использования
        system_prompt: Системный промпт (опционально, если не указан, загружается из файла)
    
    Returns:
        Ответ от модели (сырой текст с тегами)
    """
    try:
        # Формируем список сообщений
        chat_messages = []
        
        # Используем системный промпт из параметра или загружаем из файла
        if system_prompt is None:
            system_prompt = load_system_prompt()
        
        # Добавляем системный промпт если есть
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})
        
        # Добавляем сообщения из истории
        chat_messages.extend(messages)
        
        # Отправляем запрос
        completion = client.chat.completions.create(
            model=model,
            messages=chat_messages,
        )
        
        response_text = completion.choices[0].message.content
        return response_text
        
    except Exception as e:
        raise Exception(f"Error communicating with OpenRouter: {str(e)}")


def parse_assistant_response(response: str) -> List[ParsedMessage]:
    """
    Парсит ответ ассистента и преобразует в список типированных сообщений
    
    Args:
        response: Ответ от AI с тегами
        
    Returns:
        Список ParsedMessage объектов
    """
    return parse_ai_response(response)

