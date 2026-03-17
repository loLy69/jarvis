"""
Запуск бота через прокси/VPN
"""
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import Config
from database import db
from handlers.start import start_router
from handlers.ai_chat import ai_chat_router
from handlers.notes import notes_router
from handlers.reminders import reminders_router
from handlers.schedule import schedule_router
from handlers.music import music_router
from handlers.auth import auth_router
from services.scheduler import init_scheduler, get_scheduler

# Устанавливаем прокси если есть
import requests
import spotipy

# Настройка прокси для Spotify (если нужно)
proxy_settings = {
    'http': os.getenv('HTTP_PROXY'),
    'https': os.getenv('HTTPS_PROXY')
}

if proxy_settings['http'] or proxy_settings['https']:
    print(f"Используем прокси: {proxy_settings}")
    # Можно настроить spotipy для работы через прокси
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    try:
        # Проверка переменных окружения
        if not Config.BOT_TOKEN:
            logger.error("ERROR: BOT_TOKEN не найден в переменных окружения")
            return
        
        # Подключение к базе данных
        await db.connect()
        logger.info("OK: База данных готова")
        
        # Создаем экземпляр бота
        bot = Bot(token=Config.BOT_TOKEN)
        
        # Создаем диспетчер
        dp = Dispatcher()
        
        # Подключаем роутеры
        dp.include_router(start_router)
        dp.include_router(ai_chat_router)
        dp.include_router(notes_router)
        dp.include_router(reminders_router)
        dp.include_router(schedule_router)
        dp.include_router(music_router)
        dp.include_router(auth_router)
        
        # Инициализируем планировщик
        scheduler = init_scheduler(bot)
        scheduler.start()
        
        logger.info("Бот JARVIS запускается...")
        
        # Запускаем бота
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"ERROR: Критическая ошибка при запуске бота: {e}")
        raise
    
    finally:
        # Закрываем соединение с базой данных при завершении
        if db.pool:
            await db.disconnect()
        
        # Останавливаем планировщик
        scheduler = get_scheduler()
        if scheduler:
            scheduler.stop()
            
        logger.info("Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
    except Exception as e:
        print(f"ERROR: Непредвиденная ошибка: {e}")
