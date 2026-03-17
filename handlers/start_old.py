"""
Обработчики команды /start
"""
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from database import db

# Создаем роутер для обработчиков команды /start
start_router = Router()


@start_router.message(CommandStart())
async def handle_start(message: types.Message):
    """
    Обработчик команды /start
    Приветствует пользователя и регистрирует его в базе данных
    """
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    try:
        # Регистрируем пользователя в базе данных
        is_new_user = await db.register_user(user_id, username, first_name)
        
        if is_new_user:
            welcome_text = f"""
🤖 *Добро пожаловать в JARVIS!*

Я ваш персональный ИИ-ассистент. Рад знакомству, {first_name}!

💬 Просто отправьте мне любое сообщение, и я с радостью вам помогу.

🔹 /start - это приветственное сообщение
🔹 /clear - очистить историю нашего диалога

Давайте начнем наше увлекательное общение! 🚀
            """
        else:
            welcome_text = f"""
👋 *С возвращением, {first_name}!*

Рад снова вас видеть! JARVS к вашим услугам.

💬 Отправьте мне любое сообщение, и я с радостью вам помогу.

🔹 /clear - очистить историю нашего диалога

Чем могу быть полезен сегодня? 🤖
            """
        
        await message.answer(
            welcome_text
        )
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /start: {e}")
        await message.answer(
            "ERROR: Произошла ошибка. Пожалуйста, попробуйте позже."
        )
