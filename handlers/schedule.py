"""
Обработчики для работы с Google Calendar
"""
import re
from datetime import datetime
from aiogram import Router, types, F
from aiogram.filters import Command
from services.calendar import calendar_service

# Создаем роутер для обработчиков расписания
schedule_router = Router()

@schedule_router.message(Command("test_schedule"))
async def handle_test_schedule(message: types.Message):
    """Тестовая команда для расписания"""
    await message.answer("✅ Расписание работает!")


@schedule_router.message(Command("today"))
async def handle_today_events(message: types.Message):
    """
    Обработчик команды /today - показать события на сегодня
    """
    try:
        # Получаем события на сегодня
        events = await calendar_service.get_today_events()
        
        if not events:
            await message.answer("📅 Сегодня свободный день. Наслаждайся.")
            return
        
        # Формируем ответ
        today = datetime.now()
        day_name = today.strftime('%A')
        date_str = today.strftime('%d.%m.%Y')
        
        response = f"📅 Сегодня, {day_name} {date_str}\n\n"
        
        for event in events:
            response += f"{event['time']} — {event['title']}\n"
        
        response += f"\nВсего событий: {len(events)}"
        
        await message.answer(response)
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /today: {e}")
        await message.answer(
            "ERROR: Не удалось загрузить события. Проверьте настройки Google Calendar."
        )


@schedule_router.message(Command("week"))
async def handle_week_events(message: types.Message):
    """
    Обработчик команды /week - показать события на неделю
    """
    try:
        # Получаем события на неделю
        week_events = await calendar_service.get_week_events()
        
        if not week_events:
            await message.answer("📅 На ближайшие 7 дней нет событий.")
            return
        
        # Формируем ответ
        response = "📅 *События на ближайшие 7 дней:*\n\n"
        
        # Сортируем по дате
        sorted_dates = sorted(week_events.keys())
        
        for date_str in sorted_dates:
            day_data = week_events[date_str]
            response += f"*{day_data['day']} {day_data['day_name']}*\n"
            
            if not day_data['events']:
                response += "   Свободный день\n"
            else:
                for event in day_data['events']:
                    response += f"   {event['time']} — {event['title']}\n"
            
            response += "\n"
        
        await message.answer(response)
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /week: {e}")
        await message.answer(
            "ERROR: Не удалось загрузить события. Проверьте настройки Google Calendar."
        )


@schedule_router.message(Command("add_event"))
async def handle_add_event(message: types.Message):
    """
    Обработчик команды /add_event - создать новое событие
    """
    text = message.text
    
    # Получаем параметры после команды
    parts = text.replace('/add_event', '').strip().split(maxsplit=2)
    
    if len(parts) < 3:
        await message.answer(
            "📅 Использование: /add_event <дата> <время> <название>\n"
            "Примеры:\n"
            "• /add_event 20.03 15:00 Встреча с клиентом\n"
            "• /add_event 20.03.2024 15:00 Встреча с клиентом\n\n"
            "Форматы:\n"
            "• Дата: DD.MM или DD.MM.YYYY\n"
            "• Время: HH:MM\n"
            "• Длительность: 1 час по умолчанию"
        )
        return
    
    date_str = parts[0].strip()
    time_str = parts[1].strip()
    title = parts[2].strip()
    
    # Валидация форматов
    if not re.match(r'^\d{1,2}\.\d{1,2}(\.\d{4})?$', date_str):
        await message.answer("❌ Неверный формат даты. Используйте DD.MM или DD.MM.YYYY")
        return
    
    if not re.match(r'^\d{1,2}:\d{2}$', time_str):
        await message.answer("❌ Неверный формат времени. Используйте HH:MM")
        return
    
    try:
        # Создаем событие
        success = await calendar_service.create_event(date_str, time_str, title)
        
        if success:
            await message.answer(
                f"✅ Событие создано!\n"
                f"📅 {date_str} в {time_str}\n"
                f"📝 {title}"
            )
        else:
            await message.answer(
                "❌ Не удалось создать событие. "
                "Проверьте формат данных и настройки Google Calendar."
            )
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /add_event: {e}")
        await message.answer(
            "ERROR: Не удалось создать событие. Попробуйте еще раз."
        )
