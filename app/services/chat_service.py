from typing import List, Dict, Any
from openai import OpenAI
from app.core.config import settings

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
)

async def send_chat_message(
    messages: List[Dict[str, str]],
    model: str = "nvidia/nemotron-nano-12b-v2-vl:free",
    system_prompt: str = None
) -> str:
    """
    Отправляет сообщения в OpenRouter и возвращает ответ
    
    Args:
        messages: Список сообщений в формате [{"role": "user", "content": "text"}]
        model: Модель для использования
        system_prompt: Системный промпт (опционально)
    
    Returns:
        Ответ от модели
    """
    try:
        # Формируем список сообщений
        chat_messages = []
        
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

