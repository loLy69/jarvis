"""
Обработчики для работы с расписанием
"""
import re
from datetime import datetime, date, time, timedelta
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from database import db
from config import Config

schedule_router = Router()

def parse_date(date_str: str) -> date:
    """Парсит дату из строки"""
    today = date.today()
    date_str = date_str.lower().strip()
    
    if date_str == "сегодня":
        return today
    elif date_str == "завтра":
        return today + timedelta(days=1)
    elif date_str == "послезавтра":
        return today + timedelta(days=2)
    else:
        # Пробуем парсить DD.MM или DD.MM.YYYY
        patterns = [
            r"(\d{2})\.(\d{2})\.(\d{4})",  # DD.MM.YYYY
            r"(\d{2})\.(\d{2})",           # DD.MM
        ]
        
        for pattern in patterns:
            match = re.match(pattern, date_str)
            if match:
                groups = match.groups()
                if len(groups) == 3:  # DD.MM.YYYY
                    day, month, year = map(int, groups)
                    return date(year, month, day)
                else:  # DD.MM
                    day, month = map(int, groups)
                    year = today.year
                    # Если дата уже прошла в этом году, берем следующий год
                    try:
                        result = date(year, month, day)
                        if result < today:
                            year += 1
                        return date(year, month, day)
                    except ValueError:
                        pass
    
    raise ValueError(f"Неверный формат даты: {date_str}")

def parse_time(time_str: str) -> Optional[time]:
    """Парсит время из строки"""
    if not time_str:
        return None
    
    time_str = time_str.strip()
    patterns = [
        r"(\d{1,2}):(\d{2})",  # HH:MM
        r"(\d{1,2})",         # HH
    ]
    
    for pattern in patterns:
        match = re.match(pattern, time_str)
        if match:
            groups = match.groups()
            if len(groups) == 2:  # HH:MM
                hour, minute = map(int, groups)
            else:  # HH
                hour = int(groups[0])
                minute = 0
            
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return time(hour, minute)
    
    return None

@schedule_router.message(Command("today"))
async def handle_today(message: types.Message):
    """Показать события на сегодня"""
    try:
        today = date.today()
        events = await db.get_events_by_date(message.from_user.id, today)
        
        if not events:
            await message.answer("📅 На сегодня нет событий")
            return
        
        response = f"📅 **События на {today.strftime('%d.%m.%Y')}**\n\n"
        
        for event in events:
            response += f"• **{event['title']}**"
            if event['event_time']:
                response += f" - {event['event_time']}"
            response += "\n"
            if event['description']:
                response += f"  _{event['description']}_\n"
            response += "\n"
        
        await message.answer(response)
        
    except Exception as e:
        print(f"ERROR: Ошибка в /today: {e}")
        await message.answer("❌ Ошибка получения событий")

@schedule_router.message(Command("week"))
async def handle_week(message: types.Message):
    """Показать события на ближайшие 7 дней"""
    try:
        today = date.today()
        end_date = today + timedelta(days=6)
        
        events = await db.get_events(message.from_user.id, today, end_date)
        
        if not events:
            await message.answer("📅 На ближайшую неделю нет событий")
            return
        
        # Группируем по дням
        events_by_day = {}
        for event in events:
            event_date = event['event_date']
            if event_date not in events_by_day:
                events_by_day[event_date] = []
            events_by_day[event_date].append(event)
        
        response = f"📅 **События на неделю**\n\n"
        
        current_date = today
        while current_date <= end_date:
            date_str = current_date.strftime('%d.%m.%Y')
            day_name = current_date.strftime('%A')
            
            if current_date in events_by_day:
                response += f"**{date_str} ({day_name})**\n"
                for event in events_by_day[current_date]:
                    response += f"• **{event['title']}**"
                    if event['event_time']:
                        response += f" - {event['event_time']}"
                    response += "\n"
                    if event['description']:
                        response += f"  _{event['description']}_\n"
                    response += "\n"
            else:
                response += f"**{date_str} ({day_name})** - нет событий\n\n"
            
            current_date += timedelta(days=1)
        
        await message.answer(response)
        
    except Exception as e:
        print(f"ERROR: Ошибка в /week: {e}")
        await message.answer("❌ Ошибка получения событий")

@schedule_router.message(Command("add_event"))
async def handle_add_event(message: types.Message):
    """Добавить событие"""
    try:
        # Разбираем команду
        text = message.text.replace('/add_event', '').strip()
        if not text:
            await message.answer(
                "Использование:\n"
                "/add_event <дата> <время> <название>\n"
                "Форматы даты: сегодня, завтра, DD.MM, DD.MM.YYYY\n"
                "Время опционально: HH:MM\n"
                "\nПримеры:\n"
                "/add_event сегодня 15:00 Звонок клиенту\n"
                "/add_event завтра Сдать задание\n"
                "/add_event 25.03 18:00 День рождения"
            )
            return
        
        # Парсим дату, время и название
        parts = text.split()
        if len(parts) < 2:
            await message.answer("❌ Неверный формат. Укажите дату и название")
            return
        
        # Определяем где заканчивается дата
        date_part = parts[0]
        time_part = None
        title_parts = []
        
        # Проверяем есть ли время
        if len(parts) >= 3 and re.match(r'\d{1,2}:\d{2}', parts[1]):
            date_part = parts[0]
            time_part = parts[1]
            title_parts = parts[2:]
        elif len(parts) >= 2 and re.match(r'\d{1,2}', parts[1]) and len(parts) > 2:
            # Проверяем если второй параметр - время без минут
            try:
                int(parts[1])
                date_part = parts[0]
                time_part = parts[1]
                title_parts = parts[2:]
            except ValueError:
                date_part = parts[0]
                title_parts = parts[1:]
        else:
            title_parts = parts[1:]
        
        # Парсим дату
        try:
            event_date = parse_date(date_part)
        except ValueError:
            await message.answer(f"❌ Неверный формат даты: {date_part}")
            return
        
        # Парсим время
        event_time = None
        if time_part:
            try:
                event_time = parse_time(time_part)
            except ValueError:
                await message.answer(f"❌ Неверный формат времени: {time_part}")
                return
        
        # Собираем название
        title = " ".join(title_parts).strip()
        if not title:
            await message.answer("❌ Укажите название события")
            return
        
        # Добавляем в базу
        success = await db.add_event(
            message.from_user.id,
            title,
            event_date,
            event_time
        )
        
        if success:
            date_str = event_date.strftime('%d.%m.%Y')
            time_str = f" {event_time}" if event_time else ""
            await message.answer(f"✅ Событие добавлено:\n📅 {date_str}{time_str}\n📝 {title}")
        else:
            await message.answer("❌ Ошибка добавления события")
            
    except Exception as e:
        print(f"ERROR: Ошибка в /add_event: {e}")
        await message.answer("❌ Ошибка добавления события")

@schedule_router.message(Command("del_event"))
async def handle_delete_event(message: types.Message):
    """Удалить событие"""
    try:
        text = message.text.replace('/del_event', '').strip()
        
        if not text:
            # Показываем список событий для выбора
            events = await db.get_events(message.from_user.id)
            
            if not events:
                await message.answer("❌ У вас нет событий")
                return
            
            response = "📅 **Ваши события:**\n\n"
            keyboard = []
            
            for event in events[:10]:  # Показываем первые 10
                date_str = event['event_date'].strftime('%d.%m.%Y')
                time_str = f" {event['event_time']}" if event['event_time'] else ""
                response += f"ID: {event['id']} - {date_str}{time_str} - {event['title']}\n"
                keyboard.append([InlineKeyboardButton(
                    f"🗑️ {event['title']}", 
                    callback_data=f"del_event_{event['id']}"
                )])
            
            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            await message.answer(response, reply_markup=reply_markup)
            return
        
        # Пробуем удалить по ID
        try:
            event_id = int(text)
        except ValueError:
            await message.answer("❌ Укажите ID события")
            return
        
        success = await db.delete_event(event_id, message.from_user.id)
        
        if success:
            await message.answer(f"✅ Событие {event_id} удалено")
        else:
            await message.answer(f"❌ Событие {event_id} не найдено")
            
    except Exception as e:
        print(f"ERROR: Ошибка в /del_event: {e}")
        await message.answer("❌ Ошибка удаления события")

@schedule_router.callback_query(lambda query: query.data.startswith('del_event_'))
async def handle_delete_event_callback(callback_query: types.CallbackQuery):
    """Обработчик кнопок удаления событий"""
    try:
        event_id = int(callback_query.data.split('_')[2])
        
        success = await db.delete_event(event_id, callback_query.from_user.id)
        
        if success:
            await callback_query.answer(f"✅ Событие {event_id} удалено", show_alert=True)
            await callback_query.message.edit_text(f"✅ Событие {event_id} удалено")
        else:
            await callback_query.answer("❌ Событие не найдено", show_alert=True)
            
    except Exception as e:
        print(f"ERROR: Ошибка в callback удаления: {e}")
        await callback_query.answer("❌ Ошибка удаления", show_alert=True)
