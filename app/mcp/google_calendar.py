"""
Google Calendar MCP Server
Предоставляет инструменты для работы с Google Calendar через Model Context Protocol
"""
import os
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Если изменяются SCOPES, удалите файл token.json
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarMCP:
    """MCP сервер для работы с Google Calendar"""

    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Аутентификация с Google Calendar API"""
        creds = None

        # Токен хранит access и refresh токены пользователя
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # Если нет валидных credentials, авторизуем пользователя
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Файл credentials.json не найден по пути: {self.credentials_path}\n"
                        "Получите credentials в Google Cloud Console:\n"
                        "https://console.cloud.google.com/apis/credentials"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Сохраняем credentials для следующего запуска
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('calendar', 'v3', credentials=creds)

    def get_tools(self) -> List[Dict[str, Any]]:
        """Возвращает список доступных MCP инструментов"""
        return [
            {
                "name": "list_events",
                "description": "Получить список событий из календаря",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "calendar_id": {
                            "type": "string",
                            "description": "ID календаря (по умолчанию 'primary')",
                            "default": "primary"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Максимальное количество событий",
                            "default": 10
                        },
                        "time_min": {
                            "type": "string",
                            "description": "Начало периода (ISO 8601 формат)",
                        },
                        "time_max": {
                            "type": "string",
                            "description": "Конец периода (ISO 8601 формат)",
                        }
                    }
                }
            },
            {
                "name": "create_event",
                "description": "Создать новое событие в календаре",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Название события"
                        },
                        "description": {
                            "type": "string",
                            "description": "Описание события"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Время начала (ISO 8601)"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "Время окончания (ISO 8601)"
                        },
                        "timezone": {
                            "type": "string",
                            "description": "Временная зона (например, 'Europe/Moscow')",
                            "default": "UTC"
                        },
                        "attendees": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Список email участников"
                        },
                        "calendar_id": {
                            "type": "string",
                            "description": "ID календаря",
                            "default": "primary"
                        }
                    },
                    "required": ["summary", "start_time", "end_time"]
                }
            },
            {
                "name": "update_event",
                "description": "Обновить существующее событие",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "ID события"
                        },
                        "summary": {
                            "type": "string",
                            "description": "Новое название"
                        },
                        "description": {
                            "type": "string",
                            "description": "Новое описание"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Новое время начала"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "Новое время окончания"
                        },
                        "calendar_id": {
                            "type": "string",
                            "default": "primary"
                        }
                    },
                    "required": ["event_id"]
                }
            },
            {
                "name": "delete_event",
                "description": "Удалить событие из календаря",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "ID события"
                        },
                        "calendar_id": {
                            "type": "string",
                            "default": "primary"
                        }
                    },
                    "required": ["event_id"]
                }
            },
            {
                "name": "find_free_time",
                "description": "Найти свободное время в календаре",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Длительность встречи в минутах"
                        },
                        "date": {
                            "type": "string",
                            "description": "Дата для поиска (YYYY-MM-DD)"
                        },
                        "calendar_id": {
                            "type": "string",
                            "default": "primary"
                        }
                    },
                    "required": ["duration_minutes", "date"]
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнить MCP инструмент"""
        try:
            if tool_name == "list_events":
                return self.list_events(**arguments)
            elif tool_name == "create_event":
                return self.create_event(**arguments)
            elif tool_name == "update_event":
                return self.update_event(**arguments)
            elif tool_name == "delete_event":
                return self.delete_event(**arguments)
            elif tool_name == "find_free_time":
                return self.find_free_time(**arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    def list_events(
        self,
        calendar_id: str = "primary",
        max_results: int = 10,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получить список событий"""
        try:
            if not time_min:
                time_min = datetime.utcnow().isoformat() + 'Z'

            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            return {
                "success": True,
                "count": len(events),
                "events": [
                    {
                        "id": event['id'],
                        "summary": event.get('summary', 'Без названия'),
                        "start": event['start'].get('dateTime', event['start'].get('date')),
                        "end": event['end'].get('dateTime', event['end'].get('date')),
                        "description": event.get('description', ''),
                        "attendees": [a.get('email') for a in event.get('attendees', [])]
                    }
                    for event in events
                ]
            }
        except HttpError as error:
            return {"success": False, "error": str(error)}

    def create_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: str = "",
        timezone: str = "UTC",
        attendees: Optional[List[str]] = None,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Создать новое событие"""
        try:
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': timezone,
                },
            }

            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]

            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()

            return {
                "success": True,
                "event_id": created_event['id'],
                "link": created_event.get('htmlLink'),
                "message": f"Событие '{summary}' создано успешно"
            }
        except HttpError as error:
            return {"success": False, "error": str(error)}

    def update_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
        **kwargs
    ) -> Dict[str, Any]:
        """Обновить существующее событие"""
        try:
            # Получаем текущее событие
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            # Обновляем поля
            if 'summary' in kwargs:
                event['summary'] = kwargs['summary']
            if 'description' in kwargs:
                event['description'] = kwargs['description']
            if 'start_time' in kwargs:
                event['start']['dateTime'] = kwargs['start_time']
            if 'end_time' in kwargs:
                event['end']['dateTime'] = kwargs['end_time']

            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()

            return {
                "success": True,
                "event_id": updated_event['id'],
                "message": "Событие обновлено успешно"
            }
        except HttpError as error:
            return {"success": False, "error": str(error)}

    def delete_event(
        self,
        event_id: str,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Удалить событие"""
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            return {
                "success": True,
                "message": f"Событие {event_id} удалено успешно"
            }
        except HttpError as error:
            return {"success": False, "error": str(error)}

    def find_free_time(
        self,
        duration_minutes: int,
        date: str,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Найти свободное время в календаре"""
        try:
            # Парсим дату
            target_date = datetime.fromisoformat(date)
            time_min = target_date.replace(hour=9, minute=0).isoformat() + 'Z'
            time_max = target_date.replace(hour=18, minute=0).isoformat() + 'Z'

            # Получаем события на день
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # Находим свободные слоты
            free_slots = []
            current_time = datetime.fromisoformat(time_min.replace('Z', ''))
            end_time = datetime.fromisoformat(time_max.replace('Z', ''))

            for event in events:
                event_start = datetime.fromisoformat(
                    event['start'].get('dateTime', event['start'].get('date')).replace('Z', '')
                )

                # Если есть свободное время до следующего события
                if (event_start - current_time).total_seconds() / 60 >= duration_minutes:
                    free_slots.append({
                        "start": current_time.isoformat(),
                        "end": event_start.isoformat(),
                        "duration_minutes": int((event_start - current_time).total_seconds() / 60)
                    })

                event_end = datetime.fromisoformat(
                    event['end'].get('dateTime', event['end'].get('date')).replace('Z', '')
                )
                current_time = max(current_time, event_end)

            # Проверяем время после последнего события
            if (end_time - current_time).total_seconds() / 60 >= duration_minutes:
                free_slots.append({
                    "start": current_time.isoformat(),
                    "end": end_time.isoformat(),
                    "duration_minutes": int((end_time - current_time).total_seconds() / 60)
                })

            return {
                "success": True,
                "date": date,
                "requested_duration": duration_minutes,
                "free_slots": free_slots,
                "count": len(free_slots)
            }
        except Exception as error:
            return {"success": False, "error": str(error)}

