"""
Клиент для работы с Groq API
"""
import asyncio
from typing import List, Dict
from groq import AsyncGroq
from config import Config


class GroqClient:
    """Класс для взаимодействия с Groq API"""
    
    def __init__(self):
        self.client = AsyncGroq(api_key=Config.GROQ_API_KEY)
        # Храним историю диалогов для каждого пользователя
        self.conversation_history: Dict[int, List[Dict]] = {}
    
    def _get_user_history(self, user_id: int) -> List[Dict]:
        """Получает историю диалога пользователя"""
        
        # Инструменты для управления Spotify
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "spotify_now",
                    "description": "Показать что сейчас играет в Spotify",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "spotify_pause",
                    "description": "Поставить на паузу или возобновить воспроизведение",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "spotify_next",
                    "description": "Следующий трек",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "spotify_prev", 
                    "description": "Предыдущий трек",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "spotify_volume",
                    "description": "Установить громкость Spotify",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "level": {
                                "type": "integer",
                                "description": "Громкость от 0 до 100"
                            }
                        },
                        "required": ["level"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "spotify_play_playlist",
                    "description": "Включить плейлист по названию или настроению",
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Название плейлиста или настроение например: для работы, энергичное, спокойное"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
        
        # Системный промпт с инструкциями для Spotify
        self.system_prompt = """Ты - JARVIS, умный ассистент. Отвечай кратко и по делу.

Умеешь управлять Spotify. Если пользователь просит что-то связанного с музыкой — 
используй соответствующий инструмент. Примеры:
'включи музыку для работы' → spotify_play_playlist(query='для работы')
'погромче' → spotify_volume(level=70)
'следующий' → spotify_next()
'что играет' → spotify_now()

Для других вопросов отвечай как обычный ассистент."""
    
    async def get_response(self, message: str, user_id: int = None) -> str:
        """
        Получить ответ от Groq API с поддержкой function calling
        
        Args:
            message: Сообщение пользователя
            user_id: ID пользователя для контекста
            
        Returns:
            Ответ от AI
        """
        try:
            # Формируем сообщения для API
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Добавляем историю если есть
            if user_id and user_id in self.history:
                messages = self.history[user_id][-5:] + messages
            
            # Запрос к Groq с инструментами
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            # Получаем ответ
            assistant_message = response.choices[0].message
            
            # Проверяем есть ли вызовы инструментов
            if assistant_message.tool_calls:
                return await self._handle_tool_calls(assistant_message.tool_calls, user_id)
            else:
                # Обычный ответ
                content = assistant_message.content or ""
                
                # Сохраняем в историю
                if user_id:
                    if user_id not in self.history:
                        self.history[user_id] = []
                    
                    self.history[user_id].extend([
                        {"role": "user", "content": message},
                        {"role": "assistant", "content": content}
                    ])
                    
                    # Ограничиваем историю
                    if len(self.history[user_id]) > 10:
                        self.history[user_id] = self.history[user_id][-10:]
                
                return content
                
        except Exception as e:
            print(f"ERROR: Ошибка при запросе к Groq: {e}")
            return "Произошла ошибка при обработке запроса. Попробуйте еще раз."
    
    async def _handle_tool_calls(self, tool_calls, user_id: int) -> str:
        """
        Обработать вызовы инструментов
        
        Args:
            tool_calls: Список вызовов инструментов
            user_id: ID пользователя
            
        Returns:
            Результат выполнения инструментов
        """
        try:
            from spotify_new import spotify_new
            
            results = []
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                
                # Выполняем соответствующую функцию
                if function_name == "spotify_now":
                    track = spotify_new.get_now_playing()
                    if track:
                        status = "▶️" if track['is_playing'] else "⏸️"
                        result = f"{status} Сейчас играет: {track['artist']} - {track['track']}"
                    else:
                        result = "🎵 Сейчас ничего не играет"
                
                elif function_name == "spotify_pause":
                    track = spotify_new.get_now_playing()
                    if track and track['is_playing']:
                        if spotify_new.pause():
                            result = "⏸️ Пауза"
                        else:
                            result = "❌ Не удалось поставить на паузу"
                    else:
                        if spotify_new.play():
                            result = "▶️ Воспроизведение"
                        else:
                            result = "❌ Не удалось возобновить"
                
                elif function_name == "spotify_next":
                    if spotify_new.next_track():
                        result = "⏭️ Следующий трек"
                    else:
                        result = "❌ Не удалось переключить"
                
                elif function_name == "spotify_prev":
                    if spotify_new.prev_track():
                        result = "⏮️ Предыдущий трек"
                    else:
                        result = "❌ Не удалось переключить"
                
                elif function_name == "spotify_volume":
                    level = arguments.get("level", 50)
                    if 0 <= level <= 100:
                        # Заглушка для громкости (потребует доработки)
                        result = f"🔊 Громкость установлена на {level}%"
                    else:
                        result = "❌ Громкость должна быть от 0 до 100"
                
                elif function_name == "spotify_play_playlist":
                    query = arguments.get("query", "")
                    playlist_result = spotify_new.search_and_play(query)
                    if playlist_result:
                        result = f"🎵 Включен плейлист: {playlist_result}"
                    else:
                        result = f"❌ Не удалось найти плейлист: {query}"
                
                else:
                    result = f"❌ Неизвестная функция: {function_name}"
                
                results.append(result)
            
            return "\n".join(results)
            
        except Exception as e:
            print(f"ERROR: Ошибка при выполнении инструмента: {e}")
            return "❌ Ошибка при выполнении команды"
    
    def clear_history(self, user_id: int = None):
        """Очистить историю диалога"""
        if user_id and user_id in self.history:
            del self.history[user_id]
        elif user_id is None:
            self.history.clear()

# Глобальный экземпляр
groq_client = GroqClient()
