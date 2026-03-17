"""
Обработчики для работы с заметками
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from database import db

# Создаем роутер для обработчиков заметок
notes_router = Router()

@notes_router.message(Command("test_notes"))
async def handle_test_notes(message: types.Message):
    """Тестовая команда для заметок"""
    await message.answer("✅ Заметки работают!")


@notes_router.message(Command("note"))
async def handle_add_note(message: types.Message):
    """
    Обработчик команды /note - быстро сохранить заметку
    """
    user_id = message.from_user.id
    text = message.text
    
    # Получаем текст после команды
    note_text = text.replace('/note', '').strip()
    
    if not note_text:
        await message.answer(
            "📝 Использование: /note <текст заметки>\n"
            "Пример: /note Купить молоко и хлеб по дороге домой"
        )
        return
    
    try:
        # Заголовок - первые 5 слов
        words = note_text.split()
        title = ' '.join(words[:5]) + ('...' if len(words) > 5 else '')
        
        # Добавляем заметку в базу
        note_id = await db.add_note(user_id, title, note_text)
        
        await message.answer(
            f"✅ Заметка сохранена (ID: {note_id})\n"
            f"📌 {title}"
        )
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /note: {e}")
        await message.answer(
            "ERROR: Не удалось сохранить заметку. Попробуйте еще раз."
        )


@notes_router.message(Command("notes"))
async def handle_show_notes(message: types.Message):
    """
    Обработчик команды /notes - показать последние 10 заметок
    """
    user_id = message.from_user.id
    
    try:
        # Получаем последние 10 заметок
        notes = await db.get_user_notes(user_id, 10)
        
        if not notes:
            await message.answer("📝 У вас пока нет заметок.")
            return
        
        # Формируем список заметок
        response = "📝 *Ваши последние заметки:*\n\n"
        
        for i, note in enumerate(notes, 1):
            response += f"*{i}. {note['title']}* (ID: {note['id']})\n"
            response += f"📅 {note['created_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
        
        response += "💡 Для поиска: /note_find <запрос>\n"
        response += "🗑️ Для удаления: /note_del <id>"
        
        await message.answer(response)
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /notes: {e}")
        await message.answer(
            "ERROR: Не удалось загрузить заметки. Попробуйте еще раз."
        )


@notes_router.message(Command("note_find"))
async def handle_find_notes(message: types.Message):
    """
    Обработчик команды /note_find - поиск по заметкам
    """
    user_id = message.from_user.id
    text = message.text
    
    # Получаем поисковый запрос
    query = text.replace('/note_find', '').strip()
    
    if not query:
        await message.answer(
            "🔍 Использование: /note_find <запрос>\n"
            "Пример: /note_find молоко"
        )
        return
    
    try:
        # Ищем заметки
        notes = await db.search_notes(user_id, query)
        
        if not notes:
            await message.answer(f"🔍 Заметки по запросу «{query}» не найдены.")
            return
        
        # Формируем результат поиска
        response = f"🔍 *Найдено заметок: {len(notes)}*\n\n"
        
        for i, note in enumerate(notes, 1):
            response += f"*{i}. {note['title']}* (ID: {note['id']})\n"
            response += f"📅 {note['created_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
        
        await message.answer(response)
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /note_find: {e}")
        await message.answer(
            "ERROR: Не удалось выполнить поиск. Попробуйте еще раз."
        )


@notes_router.message(Command("note_del"))
async def handle_delete_note(message: types.Message):
    """
    Обработчик команды /note_del - удалить заметку по ID
    """
    user_id = message.from_user.id
    text = message.text
    
    # Получаем ID заметки
    parts = text.replace('/note_del', '').strip().split()
    
    if not parts or not parts[0].isdigit():
        await message.answer(
            "🗑️ Использование: /note_del <id>\n"
            "Пример: /note_del 5\n\n"
            "💡 ID заметки можно посмотреть в списке: /notes"
        )
        return
    
    note_id = int(parts[0])
    
    try:
        # Удаляем заметку
        deleted = await db.delete_note(user_id, note_id)
        
        if deleted:
            await message.answer(f"🗑️ Заметка с ID {note_id} удалена.")
        else:
            await message.answer(f"❌ Заметка с ID {note_id} не найдена.")
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /note_del: {e}")
        await message.answer(
            "ERROR: Не удалось удалить заметку. Попробуйте еще раз."
        )
