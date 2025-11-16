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
from app.services.chat_service import send_chat_message, parse_assistant_response, load_system_prompt, execute_mcp_message

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
    
    Парсит ответ AI по тегам и создает несколько сообщений в БД:
    - <text>...</text> → message_type='text'
    - <mcp>...</mcp> → message_type='mcp'
    - <file>...</file> → message_type='file'
    - <long_text>...</long_text> → message_type='long_text'
    """
    try:
        # Если chat_id не указан, создаем новый чат
        if request.chat_id is None:
            # Создаём чат и записываем системный промпт из запроса или из файла promt.md
            system_text = request.system_prompt
            if not system_text:
                # load_system_prompt вернёт '' если файл не найден
                system_text = load_system_prompt()

            chat = Chat(
                external_id=external_id,
                title=request.content[:50] + "..." if len(request.content) > 50 else request.content,
                model=request.model,
                system_prompt=system_text
            )
            db.add(chat)
            db.commit()
            db.refresh(chat)

            # Если есть системный промпт — сохраняем его как системное сообщение в БД
            if system_text:
                sys_msg = ChatMessage(
                    chat_id=chat.id,
                    role="system",
                    content=system_text,
                    message_type="text"
                )
                db.add(sys_msg)
                db.commit()
                db.refresh(sys_msg)
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
            content=request.content,
            message_type="text"
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)

        # Получаем историю сообщений для контекста (только основной контент, не типированные)
        messages_history = db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat.id
        ).order_by(ChatMessage.created_at).all()

        # Формируем историю для OpenRouter (берем содержимое, игнорируя типы)
        history = [{"role": msg.role, "content": msg.content} for msg in messages_history]

        # Отправляем запрос в OpenRouter
        assistant_response = await send_chat_message(
            messages=history,
            model=chat.model,
            system_prompt=chat.system_prompt
        )

        # Парсим ответ по тегам
        parsed_messages = parse_assistant_response(assistant_response)

        # Сохраняем каждое распарсенное сообщение
        saved_messages = []
        for parsed_msg in parsed_messages:
            assistant_message = ChatMessage(
                chat_id=chat.id,
                role="assistant",
                content=parsed_msg.content,
                message_type=parsed_msg.message_type
            )
            db.add(assistant_message)
            db.commit()
            db.refresh(assistant_message)
            saved_messages.append(ChatMessageResponse.model_validate(assistant_message))

        # Если нет распарсенных сообщений, сохраняем весь ответ как текст
        if not saved_messages:
            assistant_message = ChatMessage(
                chat_id=chat.id,
                role="assistant",
                content=assistant_response,
                message_type="text"
            )
            db.add(assistant_message)
            db.commit()
            db.refresh(assistant_message)
            saved_messages.append(ChatMessageResponse.model_validate(assistant_message))

        return SendMessageResponse(
            chat_id=chat.id,
            user_message=ChatMessageResponse.model_validate(user_message),
            assistant_message=saved_messages[0] if saved_messages else None,
            assistant_messages=saved_messages 
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.post("/messages/{message_id}/execute")
async def execute_mcp_message_by_id(
    message_id: int,
    db: Session = Depends(get_db),
    external_id: str = Depends(get_external_id)
):
    """
    Выполняет MCP сообщение по его ID.
    Сообщение должно иметь тип 'mcp' и принадлежать чату пользователя.
    """
    try:
        # Получаем сообщение из БД
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Проверяем что сообщение принадлежит чату пользователя
        chat = db.query(Chat).filter(
            Chat.id == message.chat_id,
            Chat.external_id == external_id
        ).first()
        if not chat:
            raise HTTPException(status_code=403, detail="Access denied to this message")
        
        # Проверяем что сообщение имеет тип 'mcp'
        if message.message_type != "mcp":
            raise HTTPException(
                status_code=400, 
                detail=f"Message type must be 'mcp', got '{message.message_type}'"
            )
        
        # Выполняем MCP запрос
        result = await execute_mcp_message(message.content)
        
        return {
            "message_id": message_id,
            "status": "success",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing MCP message: {str(e)}")

