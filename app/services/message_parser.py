"""
Парсер для распарсивания тегов из ответа AI
Преобразует теги <text>, <mcp>, <file>, <long_text> в отдельные сообщения
"""
import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ParsedMessage:
    """Распарсенное сообщение"""
    message_type: str  # text, mcp, file, long_text
    content: str


def parse_ai_response(response: str) -> List[ParsedMessage]:
    """
    Парсит ответ AI и разбивает его на сообщения по типам.
    
    Поддерживаемые теги:
    - <text>...</text> - обычный текст
    - <mcp>...</mcp> - JSON запрос к MCP
    - <file>...</file> - URL файла
    - <long_text>...</long_text> - большой текст
    
    Args:
        response: Ответ от AI с тегами
        
    Returns:
        Список ParsedMessage объектов
    """
    messages = []
    
    # Регулярные выражения для каждого типа тега
    patterns = [
        (r'<text>(.*?)</text>', 'text'),
        (r'<mcp>(.*?)</mcp>', 'mcp'),
        (r'<file>(.*?)</file>', 'file'),
        (r'<long_text>(.*?)</long_text>', 'long_text'),
    ]
    
    # Найдём все совпадения со своими позициями
    matches = []
    for pattern, msg_type in patterns:
        for match in re.finditer(pattern, response, re.DOTALL):
            matches.append({
                'start': match.start(),
                'end': match.end(),
                'content': match.group(1).strip(),
                'type': msg_type
            })
    
    # Сортируем по позиции появления в тексте
    matches.sort(key=lambda x: x['start'])
    
    # Преобразуем в ParsedMessage объекты
    for match in matches:
        messages.append(ParsedMessage(
            message_type=match['type'],
            content=match['content']
        ))
    
    return messages


def validate_parsed_messages(messages: List[ParsedMessage]) -> bool:
    """
    Проверяет валидность распарсенных сообщений.
    
    Args:
        messages: Список распарсенных сообщений
        
    Returns:
        True если сообщения валидны
    """
    valid_types = {'text', 'mcp', 'file', 'long_text'}
    
    for msg in messages:
        # Проверяем тип
        if msg.message_type not in valid_types:
            return False
        
        # Проверяем что контент не пустой
        if not msg.content or not msg.content.strip():
            return False
        
        # Для MCP - проверяем что это JSON
        if msg.message_type == 'mcp':
            try:
                import json
                json.loads(msg.content)
            except (json.JSONDecodeError, ValueError):
                return False
        
        # Для file - проверяем что это URL
        if msg.message_type == 'file':
            if not (msg.content.startswith('http://') or msg.content.startswith('https://')):
                return False
    
    return True


def extract_mcp_from_response(response: str) -> Dict[str, Any]:
    """
    Извлекает MCP запрос из ответа (первый найденный).
    
    Args:
        response: Ответ от AI
        
    Returns:
        Словарь с method и params или пустой словарь если не найдено
    """
    messages = parse_ai_response(response)
    
    for msg in messages:
        if msg.message_type == 'mcp':
            try:
                import json
                return json.loads(msg.content)
            except (json.JSONDecodeError, ValueError):
                continue
    
    return {}
