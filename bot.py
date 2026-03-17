"""
Основной файл бота JARVIS
Точка входа и запуск бота
"""
import asyncio
import logging
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


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """
    Основная функция запуска бота
    """
    try:
        # Проверяем конфигурацию
        Config.validate()
        logger.info("OK: Конфигурация проверена")
        
        # Подключаемся к базе данных
        await db.connect()
        await db.create_tables()
        logger.info("OK: База данных готова")
        
        # Создаем экземпляр бота
        bot = Bot(
            token=Config.BOT_TOKEN
        )
        
        # Создаем диспетчер
        dp = Dispatcher()
        
        # Подключаем роутеры (временно только start_router для теста)
        dp.include_router(start_router)
        # dp.include_router(ai_chat_router)
        # dp.include_router(notes_router)
        # dp.include_router(reminders_router)
        # dp.include_router(schedule_router)
        # dp.include_router(music_router)
        # dp.include_router(auth_router)
        
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
