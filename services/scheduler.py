"""
Планировщик для отправки напоминаний
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database import db


class ReminderScheduler:
    """Класс для управления планировщиком напоминаний"""
    
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(
            self.check_reminders,
            trigger=IntervalTrigger(minutes=1),
            id='reminder_checker'
        )
    
    async def check_reminders(self):
        """
        Проверяет и отправляет напоминания каждую минуту
        """
        try:
            # Получаем все неотправленные напоминания
            pending_reminders = await db.get_pending_reminders()
            
            for reminder in pending_reminders:
                user_id = reminder['user_id']
                reminder_text = reminder['text']
                reminder_id = reminder['id']
                
                try:
                    # Отправляем напоминание пользователю
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=f"🔔 *Напоминание:* {reminder_text}"
                    )
                    
                    # Отмечаем напоминание как выполненное
                    await db.mark_reminder_done(reminder_id)
                    print(f"OK: Напоминание {reminder_id} отправлено пользователю {user_id}")
                    
                except Exception as e:
                    print(f"ERROR: Ошибка отправки напоминания {reminder_id}: {e}")
                    
        except Exception as e:
            print(f"ERROR: Ошибка проверки напоминаний: {e}")
    
    def start(self):
        """Запускает планировщик"""
        self.scheduler.start()
        print("OK: Планировщик напоминаний запущен")
    
    def stop(self):
        """Останавливает планировщик"""
        self.scheduler.shutdown()
        print("OK: Планировщик напоминаний остановлен")


# Глобальный экземпляр планировщика
scheduler_instance = None


def init_scheduler(bot):
    """
    Инициализирует глобальный экземпляр планировщика
    
    Args:
        bot: Экземпляр бота
        
    Returns:
        ReminderScheduler: Экземпляр планировщика
    """
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = ReminderScheduler(bot)
    return scheduler_instance


def get_scheduler():
    """
    Возвращает глобальный экземпляр планировщика
    
    Returns:
        ReminderScheduler: Экземпляр планировщика или None
    """
    return scheduler_instance
