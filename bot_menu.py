"""
Настройка меню бота с кнопками
"""
from aiogram import Bot, types
from aiogram.enums import ParseMode
from config import Config
import asyncio
import sys

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

async def set_bot_menu():
    """Установить меню бота с кнопками"""
    try:
        bot = Bot(token=Config.BOT_TOKEN)
        
        # Создаем команды меню
        bot_commands = [
            types.BotCommand(command="start", description="🏠 Главное меню"),
            types.BotCommand(command="now", description="🎵 Что играет"),
            types.BotCommand(command="pause", description="⏸️ Пауза/Воспроизведение"),
            types.BotCommand(command="next", description="⏭️ Следующий трек"),
            types.BotCommand(command="prev", description="⏮️ Предыдущий трек"),
            types.BotCommand(command="note", description="📝 Создать заметку"),
            types.BotCommand(command="today", description="📅 Расписание на сегодня"),
            types.BotCommand(command="help", description="❓ Помощь"),
        ]
        
        # Устанавливаем команды
        await bot.set_my_commands(bot_commands)
        print("Меню бота установлено!")
        
        # Создаем меню кнопок (если нужно)
        menu_button = types.MenuButtonCommands()
        await bot.set_chat_menu_button(menu_button=menu_button)
        print("Кнопка меню установлена!")
        
        await bot.session.close()
        
    except Exception as e:
        print(f"Ошибка установки меню: {e}")

if __name__ == "__main__":
    asyncio.run(set_bot_menu())
