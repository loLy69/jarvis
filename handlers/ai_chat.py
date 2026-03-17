"""
Обработчики AI чата и команд управления диалогом
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from services.groq_client import groq_client

# Создаем роутер для обработчиков AI чата
ai_chat_router = Router()


@ai_chat_router.message(Command("clear"))
async def handle_clear(message: types.Message):
    """
    Обработчик команды /clear
    Очищает историю диалога пользователя
    """
    user_id = message.from_user.id
    
    try:
        # Очищаем историю диалога
        groq_client.clear_history(user_id)
        
        await message.answer(
            "История диалога очищена!\n\n"
            "Давайте начнем наш разговор с чистого листа. "
            "Что бы вы хотели обсудить?"
        )
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /clear: {e}")
        await message.answer(
            "ERROR: Произошла ошибка при очистке истории. Пожалуйста, попробуйте позже."
        )


@ai_chat_router.message(F.text)
async def handle_ai_chat(message: types.Message):
    """
    Обработчик текстовых сообщений
    Перенаправляет сообщение в Groq API для получения ответа
    """
    # Игнорируем команды (они уже обработаны другими роутерами)
    if message.text.startswith('/'):
        return
    
    try:
        # Получаем ответ от AI с поддержкой Spotify
        response = await groq_client.get_response(
            message=message.text,
            user_id=message.from_user.id
        )
        
        await message.answer(response)
        
    except Exception as e:
        print(f"ERROR: Ошибка в AI чате: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")
