from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.chat import Chat, ChatMessage
from app.schemas.chat import (
    ChatCreate, ChatResponse, ChatUpdate,
    SendMessageRequest, SendMessageResponse,
    ChatMessageResponse
)
from app.services.chat_service import send_chat_message

router = APIRouter(prefix="/chats", tags=["chats"])

def get_external_id(x_external_id: str = Header(...)) -> str:
    """Получение external_id пользователя из заголовка"""
    if not x_external_id:
        raise HTTPException(status_code=401, detail="X-External-Id header is required")
    return x_external_id

@router.post("/", response_model=ChatResponse)
async def create_chat(
    chat_data: ChatCreate,
    db: Session = Depends(get_db),
    external_id: str = Depends(get_external_id)
):
    """Создание нового чата"""
    chat = Chat(
        external_id=external_id,
        title=chat_data.title,
        model=chat_data.model,
        system_prompt=chat_data.system_prompt
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return ChatResponse.model_validate(chat)

@router.get("/", response_model=List[ChatResponse])
async def list_chats(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    external_id: str = Depends(get_external_id)
):
    """Список чатов текущего пользователя"""
    chats = db.query(Chat).filter(Chat.external_id == external_id).offset(skip).limit(limit).all()
    return [ChatResponse.model_validate(chat) for chat in chats]

@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    external_id: str = Depends(get_external_id)
):
    """Получение чата по ID"""
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.external_id == external_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return ChatResponse.model_validate(chat)

@router.patch("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: int,
    chat_update: ChatUpdate,
    db: Session = Depends(get_db),
    external_id: str = Depends(get_external_id)
):
    """Обновление чата"""
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.external_id == external_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat_update.title is not None:
        chat.title = chat_update.title
    if chat_update.system_prompt is not None:
        chat.system_prompt = chat_update.system_prompt

    db.commit()
    db.refresh(chat)

    return ChatResponse.model_validate(chat)

@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    external_id: str = Depends(get_external_id)
):
    """Удаление чата"""
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.external_id == external_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    db.delete(chat)
    db.commit()

    return {"message": "Chat deleted successfully"}

@router.post("/message", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    external_id: str = Depends(get_external_id)
):
    """
    Отправка сообщения в чат.
    Если chat_id не указан, создается новый чат.
    """
    try:
        # Если chat_id не указан, создаем новый чат
        if request.chat_id is None:
            chat = Chat(
                external_id=external_id,
                title=request.content[:50] + "..." if len(request.content) > 50 else request.content,
                model=request.model,
                system_prompt=request.system_prompt
            )
            db.add(chat)
            db.commit()
            db.refresh(chat)
        else:
            # Проверяем существует ли чат и принадлежит ли он пользователю
            chat = db.query(Chat).filter(
                Chat.id == request.chat_id,
                Chat.external_id == external_id
            ).first()
            if not chat:
                raise HTTPException(status_code=404, detail="Chat not found")

        # Сохраняем сообщение пользователя
        user_message = ChatMessage(
            chat_id=chat.id,
            role="user",
            content=request.content
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)

        # Получаем историю сообщений для контекста
        messages_history = db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat.id
        ).order_by(ChatMessage.created_at).all()

        # Формируем историю для OpenRouter
        history = [{"role": msg.role, "content": msg.content} for msg in messages_history]

        # Отправляем запрос в OpenRouter
        assistant_content = await send_chat_message(
            messages=history,
            model=chat.model,
            system_prompt=chat.system_prompt
        )

        # Сохраняем ответ ассистента
        assistant_message = ChatMessage(
            chat_id=chat.id,
            role="assistant",
            content=assistant_content
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        return SendMessageResponse(
            chat_id=chat.id,
            user_message=ChatMessageResponse.model_validate(user_message),
            assistant_message=ChatMessageResponse.model_validate(assistant_message)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

