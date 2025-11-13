"""
Сервис для AI-assisted планирования с использованием OpenRouter и Google Calendar MCP
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
from app.core.config import settings
from app.mcp.google_calendar import GoogleCalendarMCP


class AICalendarAssistant:
    """AI ассистент для работы с календарём через OpenRouter"""

    def __init__(self, calendar_mcp: GoogleCalendarMCP):
        self.calendar_mcp = calendar_mcp
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"

    async def process_natural_language_request(
        self,
        user_request: str,
        model: str = "nvidia/nemotron-nano-12b-v2-vl:free"
    ) -> Dict[str, Any]:
        """
        Обработать естественноязыковой запрос пользователя

        Примеры:
        - "Создай встречу завтра в 10 утра с Иваном"
        - "Когда у меня свободное время на этой неделе?"
        - "Перенеси встречу на час позже"
        """

        # Получаем список доступных инструментов
        tools = self.calendar_mcp.get_tools()

        # Формируем системный промпт с описанием инструментов
        system_prompt = self._create_system_prompt(tools)

        # Отправляем запрос в OpenRouter
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.openrouter_url,
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "Calendar AI Assistant"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_request}
                    ]
                },
                timeout=30.0
            )

            if response.status_code != 200:
                return {
                    "error": f"OpenRouter API error: {response.status_code}",
                    "details": response.text
                }

            ai_response = response.json()
            assistant_message = ai_response["choices"][0]["message"]["content"]

            # Пытаемся извлечь tool call из ответа
            tool_call = self._parse_tool_call(assistant_message)

            if tool_call:
                # Выполняем инструмент
                result = self.calendar_mcp.execute_tool(
                    tool_call["tool_name"],
                    tool_call["arguments"]
                )

                return {
                    "success": True,
                    "user_request": user_request,
                    "ai_interpretation": assistant_message,
                    "tool_executed": tool_call["tool_name"],
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "user_request": user_request,
                    "ai_response": assistant_message,
                    "message": "AI не смог определить действие"
                }

    def _create_system_prompt(self, tools: List[Dict[str, Any]]) -> str:
        """Создать системный промпт с описанием доступных инструментов"""
        tools_description = "\n\n".join([
            f"**{tool['name']}**: {tool['description']}\n"
            f"Параметры: {json.dumps(tool['input_schema']['properties'], indent=2, ensure_ascii=False)}"
            for tool in tools
        ])

        return f"""Ты - умный ассистент для управления календарём Google Calendar.

У тебя есть доступ к следующим инструментам:

{tools_description}

Когда пользователь просит что-то сделать с календарём, ты должен:
1. Понять что именно нужно сделать
2. Выбрать подходящий инструмент
3. Сформировать JSON с параметрами вызова

Формат ответа:
```json
{{
  "tool_name": "название_инструмента",
  "arguments": {{
    "параметр1": "значение1",
    "параметр2": "значение2"
  }}
}}
```

Учитывай:
- Текущая дата: {datetime.now().strftime('%Y-%m-%d')}
- Временная зона по умолчанию: Europe/Moscow
- Формат даты/времени: ISO 8601 (например, 2025-11-14T10:00:00)

Примеры:
- "Создай встречу завтра в 10 утра" → create_event
- "Покажи мои события на сегодня" → list_events  
- "Найди свободное время на час завтра" → find_free_time
- "Удали встречу с ID xyz" → delete_event
"""

    def _parse_tool_call(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """Извлечь tool call из ответа AI"""
        try:
            # Ищем JSON блок в ответе
            start = ai_response.find("{")
            end = ai_response.rfind("}") + 1

            if start >= 0 and end > start:
                json_str = ai_response[start:end]
                tool_call = json.loads(json_str)

                if "tool_name" in tool_call and "arguments" in tool_call:
                    return tool_call

            return None
        except Exception:
            return None

    async def smart_schedule_meeting(
        self,
        summary: str,
        duration_minutes: int,
        preferred_dates: List[str],
        attendees: Optional[List[str]] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Умное планирование встречи с учётом занятости

        Args:
            summary: Название встречи
            duration_minutes: Длительность в минутах
            preferred_dates: Список предпочтительных дат (YYYY-MM-DD)
            attendees: Список участников (email)
            preferences: Дополнительные предпочтения (время дня, приоритет и т.д.)
        """

        best_slot = None

        # Ищем свободное время в предпочтительные даты
        for date in preferred_dates:
            result = self.calendar_mcp.find_free_time(
                duration_minutes=duration_minutes,
                date=date
            )

            if result.get("success") and result.get("free_slots"):
                # Выбираем первый подходящий слот
                for slot in result["free_slots"]:
                    if slot["duration_minutes"] >= duration_minutes:
                        best_slot = {
                            "date": date,
                            "start": slot["start"],
                            "end": datetime.fromisoformat(slot["start"]) + timedelta(minutes=duration_minutes)
                        }
                        break

                if best_slot:
                    break

        if not best_slot:
            return {
                "success": False,
                "message": "Не найдено подходящего времени",
                "searched_dates": preferred_dates
            }

        # Создаём событие
        create_result = self.calendar_mcp.create_event(
            summary=summary,
            start_time=best_slot["start"],
            end_time=best_slot["end"].isoformat(),
            timezone="Europe/Moscow",
            attendees=attendees or []
        )

        return {
            "success": True,
            "meeting": {
                "summary": summary,
                "start": best_slot["start"],
                "end": best_slot["end"].isoformat(),
                "duration_minutes": duration_minutes
            },
            "creation_result": create_result
        }

