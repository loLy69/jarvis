"""
Обработчики для работы с напоминаниями
"""
import re
from datetime import datetime, timedelta
from aiogram import Router, types, F
from aiogram.filters import Command
from database import db

# Создаем роутер для обработчиков напоминаний
reminders_router = Router()


def parse_reminder_time(time_str: str) -> datetime:
    """
    Парсит строку времени и возвращает datetime объект
    """
    now = datetime.now()
    
    # Формат Nmin
    min_match = re.match(r'^(\d+)min$', time_str)
    if min_match:
        minutes = int(min_match.group(1))
        return now + timedelta(minutes=minutes)
    
    # Формат Nh
    hour_match = re.match(r'^(\d+)h$', time_str)
    if hour_match:
        hours = int(hour_match.group(1))
        return now + timedelta(hours=hours)
    
    # Формат HH:MM
    time_match = re.match(r'^(\d{1,2}):(\d{2})$', time_str)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        
        # Создаем datetime на сегодня
        reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Если время уже прошло, переносим на завтра
        if reminder_time <= now:
            reminder_time += timedelta(days=1)
        
        return reminder_time
    
    # Если не удалось распарсить
    raise ValueError(f"Неверный формат времени: {time_str}")


@reminders_router.message(Command("remind"))
async def handle_add_reminder(message: types.Message):
    """
    Обработчик команды /remind - создать напоминание
    """
    user_id = message.from_user.id
    text = message.text
    
    # Получаем параметры после команды
    parts = text.replace('/remind', '').strip().split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer(
            "⏰ Использование: /remind <время> <текст>\n"
            "Примеры:\n"
            "• /remind 10min позвонить маме\n"
            "• /remind 18:30 встреча\n"
            "• /remind 2h проверить почту\n\n"
            "Форматы времени: Nmin, Nh, HH:MM"
        )
        return
    
    time_str = parts[0]
    reminder_text = parts[1]
    
    try:
        # Парсим время
        remind_at = parse_reminder_time(time_str)
        
        # Добавляем напоминание в базу
        reminder_id = await db.add_reminder(user_id, reminder_text, remind_at)
        
        # Форматируем время для ответа
        time_str_formatted = remind_at.strftime('%d.%m.%Y %H:%M')
        
        await message.answer(
            f"⏰ Напоминание создано (ID: {reminder_id})\n"
            f"📅 {time_str_formatted}\n"
            f"📝 {reminder_text}"
        )
        
    except ValueError as e:
        await message.answer(f"❌ {str(e)}")
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /remind: {e}")
        await message.answer(
            "ERROR: Не удалось создать напоминание. Попробуйте еще раз."
        )


@reminders_router.message(Command("reminders"))
async def handle_show_reminders(message: types.Message):
    """
    Обработчик команды /reminders - показать активные напоминания
    """
    user_id = message.from_user.id
    
    try:
        # Получаем активные напоминания
        reminders = await db.get_user_reminders(user_id)
        
        if not reminders:
            await message.answer("⏰ У вас нет активных напоминаний.")
            return
        
        # Формируем список напоминаний
        response = "⏰ *Ваши активные напоминания:*\n\n"
        
        for reminder in reminders:
            time_str = reminder['remind_at'].strftime('%d.%m.%Y %H:%M')
            response += f"*ID {reminder['id']}:* {reminder['text']}\n"
            response += f"📅 {time_str}\n\n"
        
        response += "🗑️ Для удаления: /remind_del <id>"
        
        await message.answer(response)
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /reminders: {e}")
        await message.answer(
            "ERROR: Не удалось загрузить напоминания. Попробуйте еще раз."
        )


@reminders_router.message(Command("remind_del"))
async def handle_delete_reminder(message: types.Message):
    """
    Обработчик команды /remind_del - удалить напоминание по ID
    """
    user_id = message.from_user.id
    text = message.text
    
    # Получаем ID напоминания
    parts = text.replace('/remind_del', '').strip().split()
    
    if not parts or not parts[0].isdigit():
        await message.answer(
            "🗑️ Использование: /remind_del <id>\n"
            "Пример: /remind_del 3\n\n"
            "💡 ID напоминания можно посмотреть в списке: /reminders"
        )
        return
    
    reminder_id = int(parts[0])
    
    try:
        # Удаляем напоминание
        deleted = await db.delete_reminder(user_id, reminder_id)
        
        if deleted:
            await message.answer(f"🗑️ Напоминание с ID {reminder_id} удалено.")
        else:
            await message.answer(f"❌ Напоминание с ID {reminder_id} не найдено.")
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /remind_del: {e}")
        await message.answer(
            "ERROR: Не удалось удалить напоминание. Попробуйте еще раз."
        )
