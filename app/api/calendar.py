"""
API эндпоинты для работы с Google Calendar через MCP
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.mcp.google_calendar import GoogleCalendarMCP
from app.services.ai_calendar_service import AICalendarAssistant

router = APIRouter(prefix="/calendar", tags=["Google Calendar MCP"])

# Инициализация MCP сервера (singleton)
_calendar_mcp = None

def get_calendar_mcp() -> GoogleCalendarMCP:
    """Получить экземпляр Google Calendar MCP"""
    global _calendar_mcp
    if _calendar_mcp is None:
        try:
            _calendar_mcp = GoogleCalendarMCP()
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
    return _calendar_mcp


# === Pydantic схемы ===

class EventCreate(BaseModel):
    summary: str = Field(..., description="Название события")
    description: Optional[str] = Field("", description="Описание события")
    start_time: str = Field(..., description="Время начала (ISO 8601)")
    end_time: str = Field(..., description="Время окончания (ISO 8601)")
    timezone: str = Field("Europe/Moscow", description="Временная зона")
    attendees: Optional[List[str]] = Field(None, description="Список email участников")
    calendar_id: str = Field("primary", description="ID календаря")


class EventUpdate(BaseModel):
    event_id: str = Field(..., description="ID события")
    summary: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    calendar_id: str = "primary"


class EventList(BaseModel):
    calendar_id: str = "primary"
    max_results: int = Field(10, ge=1, le=100)
    time_min: Optional[str] = None
    time_max: Optional[str] = None


class FindFreeTime(BaseModel):
    duration_minutes: int = Field(..., ge=15, description="Длительность в минутах")
    date: str = Field(..., description="Дата для поиска (YYYY-MM-DD)")
    calendar_id: str = "primary"


class MCPToolExecute(BaseModel):
    tool_name: str = Field(..., description="Название MCP инструмента")
    arguments: Dict[str, Any] = Field(..., description="Аргументы инструмента")


# === Endpoints ===

@router.get("/tools")
async def get_available_tools(mcp: GoogleCalendarMCP = Depends(get_calendar_mcp)):
    """
    Получить список доступных MCP инструментов для Google Calendar
    """
    return {
        "service": "Google Calendar",
        "tools": mcp.get_tools()
    }


@router.post("/tools/execute")
async def execute_mcp_tool(
    request: MCPToolExecute,
    mcp: GoogleCalendarMCP = Depends(get_calendar_mcp)
):
    """
    Выполнить MCP инструмент напрямую
    """
    result = mcp.execute_tool(request.tool_name, request.arguments)

    if not result.get("success", False) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/events")
async def create_event(
    event: EventCreate,
    mcp: GoogleCalendarMCP = Depends(get_calendar_mcp)
):
    """
    Создать новое событие в Google Calendar
    """
    result = mcp.create_event(
        summary=event.summary,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        timezone=event.timezone,
        attendees=event.attendees,
        calendar_id=event.calendar_id
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create event"))

    return result


@router.get("/events")
async def list_events(
    calendar_id: str = "primary",
    max_results: int = 10,
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    mcp: GoogleCalendarMCP = Depends(get_calendar_mcp)
):
    """
    Получить список событий из Google Calendar
    """
    result = mcp.list_events(
        calendar_id=calendar_id,
        max_results=max_results,
        time_min=time_min,
        time_max=time_max
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to list events"))

    return result


@router.patch("/events/{event_id}")
async def update_event(
    event_id: str,
    event: EventUpdate,
    mcp: GoogleCalendarMCP = Depends(get_calendar_mcp)
):
    """
    Обновить существующее событие
    """
    update_data = event.model_dump(exclude_unset=True, exclude={"event_id"})
    update_data["event_id"] = event_id

    result = mcp.update_event(**update_data)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to update event"))

    return result


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: str,
    calendar_id: str = "primary",
    mcp: GoogleCalendarMCP = Depends(get_calendar_mcp)
):
    """
    Удалить событие из календаря
    """
    result = mcp.delete_event(event_id=event_id, calendar_id=calendar_id)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to delete event"))

    return result


@router.post("/find-free-time")
async def find_free_time(
    request: FindFreeTime,
    mcp: GoogleCalendarMCP = Depends(get_calendar_mcp)
):
    """
    Найти свободное время в календаре
    """
    result = mcp.find_free_time(
        duration_minutes=request.duration_minutes,
        date=request.date,
        calendar_id=request.calendar_id
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to find free time"))

    return result


@router.get("/health")
async def calendar_health_check(mcp: GoogleCalendarMCP = Depends(get_calendar_mcp)):
    """
    Проверка работоспособности Google Calendar MCP
    """
    try:
        # Пытаемся получить 1 событие для проверки
        result = mcp.list_events(max_results=1)
        return {
            "status": "ok" if result.get("success") else "error",
            "service": "Google Calendar MCP",
            "authenticated": result.get("success", False)
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "Google Calendar MCP",
            "error": str(e)
        }


# === AI-Assisted Endpoints ===

class NaturalLanguageRequest(BaseModel):
    request: str = Field(..., description="Естественноязыковой запрос")
    model: str = Field("nvidia/nemotron-nano-12b-v2-vl:free", description="Модель OpenRouter")


class SmartScheduleRequest(BaseModel):
    summary: str = Field(..., description="Название встречи")
    duration_minutes: int = Field(..., ge=15, description="Длительность в минутах")
    preferred_dates: List[str] = Field(..., description="Предпочтительные даты (YYYY-MM-DD)")
    attendees: Optional[List[str]] = Field(None, description="Участники (email)")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Дополнительные предпочтения")


@router.post("/ai/natural-language")
async def process_natural_language(
    request: NaturalLanguageRequest,
    mcp: GoogleCalendarMCP = Depends(get_calendar_mcp)
):
    """
    Обработать естественноязыковой запрос с помощью AI

    Примеры запросов:
    - "Создай встречу завтра в 10 утра с Иваном"
    - "Когда у меня свободное время на этой неделе?"
    - "Покажи мои события на сегодня"
    """
    assistant = AICalendarAssistant(mcp)
    result = await assistant.process_natural_language_request(
        user_request=request.request,
        model=request.model
    )
    return result


@router.post("/ai/smart-schedule")
async def smart_schedule_meeting(
    request: SmartScheduleRequest,
    mcp: GoogleCalendarMCP = Depends(get_calendar_mcp)
):
    """
    Умное планирование встречи с автоматическим поиском свободного времени

    AI автоматически найдёт лучшее время в предпочтительные даты
    """
    assistant = AICalendarAssistant(mcp)
    result = await assistant.smart_schedule_meeting(
        summary=request.summary,
        duration_minutes=request.duration_minutes,
        preferred_dates=request.preferred_dates,
        attendees=request.attendees,
        preferences=request.preferences
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to schedule meeting"))

    return result



