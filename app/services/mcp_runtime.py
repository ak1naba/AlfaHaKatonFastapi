"""
MCP Runtime клиент для выполнения MCP команд через внешний сервис
"""
import httpx
import json
from typing import Dict, Any, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


async def execute_mcp_command(mcp_command: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    """
    Выполняет MCP команду через MCP Runtime сервис.
    
    Args:
        mcp_command: Словарь с method и params (например {"method": "gmail.sendEmail", "params": {...}})
        timeout: Таймаут для запроса в секундах (по умолчанию 30)
        
    Returns:
        Словарь с результатом выполнения команды или объект ошибки
        
    Example:
        result = await execute_mcp_command({
            "method": "gmail.sendEmail",
            "params": {
                "to": "user@example.com",
                "subject": "Hello",
                "body": "World"
            }
        })
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.MCP_RUNTIME_URL,
                json=mcp_command,
                timeout=timeout
            )
            
            # Проверяем успешность запроса
            if response.status_code == 200:
                result = response.json()
                logger.info(f"MCP command executed successfully: {mcp_command.get('method')}")
                return result
            else:
                error_msg = f"MCP Runtime returned status {response.status_code}"
                logger.error(f"{error_msg}: {response.text}")
                return {
                    "error": error_msg,
                    "status_code": response.status_code,
                    "detail": response.text
                }
                
    except httpx.TimeoutException as e:
        error_msg = f"MCP Runtime request timeout after {timeout}s"
        logger.error(f"{error_msg}: {str(e)}")
        return {
            "error": error_msg,
            "type": "timeout"
        }
        
    except httpx.ConnectError as e:
        error_msg = f"Failed to connect to MCP Runtime at {settings.MCP_RUNTIME_URL}"
        logger.error(f"{error_msg}: {str(e)}")
        return {
            "error": error_msg,
            "type": "connection_error"
        }
        
    except json.JSONDecodeError as e:
        error_msg = "MCP Runtime returned invalid JSON"
        logger.error(f"{error_msg}: {str(e)}")
        return {
            "error": error_msg,
            "type": "invalid_json"
        }
        
    except Exception as e:
        error_msg = f"Unexpected error executing MCP command: {str(e)}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "type": "unknown_error"
        }


def format_mcp_result_for_ai(result: Dict[str, Any], method: str) -> str:
    """
    Форматирует результат MCP команды для передачи AI.
    
    Args:
        result: Результат от MCP Runtime
        method: Название метода (для логирования)
        
    Returns:
        Отформатированная строка с результатом
    """
    if "error" in result:
        return f"❌ MCP Command Failed\nMethod: {method}\nError: {result['error']}\nDetails: {result.get('detail', 'No details')}"
    
    # Успешное выполнение
    result_json = json.dumps(result, ensure_ascii=False, indent=2)
    return f"✅ MCP Command Executed\nMethod: {method}\nResult:\n{result_json}"
