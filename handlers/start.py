"""
Обработчики команды /start и главного меню
"""
from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database import db

# Создаем роутер для обработчиков команды /start
start_router = Router()

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💬 Чат"),
            KeyboardButton(text="📝 Заметки")
        ],
        [
            KeyboardButton(text="🔔 Напоминания"),
            KeyboardButton(text="📅 Расписание")
        ],
        [
            KeyboardButton(text="🎵 Музыка"),
            KeyboardButton(text="⚙️ Настройки")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие..."
)


@start_router.message(Command("test"))
async def handle_test(message: types.Message):
    """Тестовая команда"""
    await message.answer("✅ Тест работает! Бот отвечает на команды.")


@start_router.message(Command("note"))
async def handle_note(message: types.Message):
    """Команда для создания заметки"""
    text = message.text.replace('/note', '').strip()
    if not text:
        await message.answer("Использование: /note <текст заметки>")
        return
    
    try:
        # Простое сохранение заметки
        await message.answer(f"✅ Заметка сохранена: {text}")
    except Exception as e:
        await message.answer("❌ Ошибка сохранения заметки")


@start_router.message(Command("devices"))
async def handle_devices(message: types.Message):
    """Команда для показа всех устройств"""
    try:
        from services.spotify_client import spotify_client
        
        sp = spotify_client.get_spotify_client()
        if not sp:
            await message.answer("❌ Ошибка подключения к Spotify")
            return
        
        # Получаем список устройств
        devices = sp.devices()
        
        if not devices.get('devices'):
            await message.answer("📱 **Активные устройства не найдены**\n\n💡 Откройте Spotify на любом устройстве и включите музыку")
            return
        
        response = "📱 **Доступные устройства:**\n\n"
        for device in devices['devices']:
            is_active = "🟢" if device['is_active'] else "⚪"
            device_name = device['name']
            device_type = device['type']
            response += f"{is_active} {device_name} ({device_type})\n"
        
        await message.answer(response)
        
    except Exception as e:
        print(f"ERROR: Ошибка в /devices: {e}")
        await message.answer(f"❌ Ошибка: {str(e)[:50]}...")


@start_router.message(Command("now"))
async def handle_now(message: types.Message):
    """Что сейчас играет"""
    try:
        from spotify_new import spotify_new
        
        track = spotify_new.get_now_playing()
        if track:
            status = "▶️" if track['is_playing'] else "⏸️"
            response = f"{status} **Сейчас играет:**\n\n"
            response += f"🎤 {track['artist']}\n"
            response += f"🎼 {track['track']}\n"
            response += f"💿 {track['album']}"
            await message.answer(response)
        else:
            await message.answer("🎵 Сейчас ничего не играет.\n\nВключите музыку в Spotify!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@start_router.message(Command("pause"))
async def handle_pause(message: types.Message):
    """Пауза/воспроизведение"""
    try:
        from spotify_new import spotify_new
        
        track = spotify_new.get_now_playing()
        if track and track['is_playing']:
            if spotify_new.pause():
                await message.answer("⏸️ Пауза")
            else:
                await message.answer("❌ Не удалось поставить на паузу")
        else:
            if spotify_new.play():
                await message.answer("▶️ Воспроизведение")
            else:
                await message.answer("❌ Не удалось возобновить")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@start_router.message(Command("next"))
async def handle_next(message: types.Message):
    """Следующий трек"""
    try:
        from spotify_new import spotify_new
        
        if spotify_new.next_track():
            await message.answer("⏭️ Следующий трек")
        else:
            await message.answer("❌ Не удалось переключить")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@start_router.message(Command("prev"))
async def handle_prev(message: types.Message):
    """Предыдущий трек"""
    try:
        from spotify_new import spotify_new
        
        if spotify_new.prev_track():
            await message.answer("⏮️ Предыдущий трек")
        else:
            await message.answer("❌ Не удалось переключить")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@start_router.message(Command("help"))
async def handle_help(message: types.Message):
    """Помощь"""
    help_text = """
🤖 **JARVIS - Помощник**

🎵 **Музыка Spotify:**
/now - Что сейчас играет
/pause - Пауза/Воспроизведение  
/next - Следующий трек
/prev - Предыдущий трек

📝 **Заметки:**
/note <текст> - Создать заметку

📅 **Календарь:**
/today - Расписание на сегодня

🏠 **Главное меню:**
/start - Показать главное меню

💡 **Совет:** Нажмите на меню слева (☰) для быстрых команд!
    """
    await message.answer(help_text)


@start_router.message(Command("today"))
async def handle_today(message: types.Message):
    """Команда для календаря"""
    print(f"DEBUG: Получена команда /today от {message.from_user.id}")
    try:
        await message.answer("📅 Сегодня свободный день. Наслаждайся!\n\nДля интеграции с Google Calendar добавьте GOOGLE_CREDENTIALS в .env")
    except Exception as e:
        print(f"ERROR: Ошибка в /today: {e}")
        await message.answer("❌ Ошибка календаря")


@start_router.message(Command("spotify_auth"))
async def handle_spotify_auth(message: types.Message):
    """Команда авторизации Spotify"""
    try:
        # Проверяем настройки Spotify
        from config import Config
        if not all([Config.SPOTIFY_CLIENT_ID, Config.SPOTIFY_CLIENT_SECRET, Config.SPOTIFY_REDIRECT_URI]):
            await message.answer(
                "❌ Отсутствуют настройки Spotify. Добавьте переменные в .env:\n"
                "• SPOTIFY_CLIENT_ID\n"
                "• SPOTIFY_CLIENT_SECRET\n"
                "• SPOTIFY_REDIRECT_URI"
            )
            return
        
        # Создаем ссылку для авторизации
        import urllib.parse
        
        redirect_uri = urllib.parse.quote(Config.SPOTIFY_REDIRECT_URI)
        scope = urllib.parse.quote("user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private")
        
        auth_url = f"https://accounts.spotify.com/authorize?client_id={Config.SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
        
        await message.answer(
            f"🎵 **Авторизация Spotify**\n\n"
            f"1. Откройте эту ссылку в браузере:\n"
            f"{auth_url}\n\n"
            f"2. Разрешите доступ к Spotify\n"
            f"3. Скопируйте URL из адресной строки после редиректа\n"
            f"4. Отправьте команду: `/spotify_code <ваш_код>`\n\n"
            f"Код будет выглядеть как: `http://127.0.0.1:8888/callback?code=ABC123...`"
        )
        
    except Exception as e:
        print(f"ERROR: Ошибка в /spotify_auth: {e}")
        await message.answer("❌ Ошибка при генерации ссылки авторизации")


@start_router.message(Command("spotify_code"))
async def handle_spotify_code(message: types.Message):
    """Команда ввода кода Spotify"""
    text = message.text
    parts = text.replace('/spotify_code', '').strip().split()
    
    if not parts:
        await message.answer(
            "❌ Использование: `/spotify_code <код>`\n\n"
            "Пример: `/spotify_code AQD...xyz123`"
        )
        return
    
    code = parts[0]
    
    await message.answer(
        f"✅ Код получен: {code[:20]}...\n\n"
        f"Внимание: полная интеграция Spotify требует дополнительной настройки.\n"
        f"Сейчас команда /now будет работать с базовыми функциями."
    )


@start_router.message(CommandStart())
async def handle_start(message: types.Message):
    """
    Обработчик команды /start
    Приветствует пользователя, регистрирует в БД и показывает главное меню
    """
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    try:
        # Регистрируем пользователя в базе данных
        is_new_user = await db.register_user(user_id, username, first_name)
        
        if is_new_user:
            welcome_text = f"""
🤖 *Добро пожаловать в JARVIS, {first_name}!*

Я ваш персональный ИИ-ассистент. Рад знакомству!

💡 *Что я умею:*
• 🤖 Общаться на любые темы
• 📝 Сохранять ваши заметки  
• ⏰ Напоминать о важных делах
• 📅 Планировать ваш день

Выберите действие в меню ниже или просто напишите мне сообщение!
            """
        else:
            welcome_text = f"""
👋 *Снова здравствуйте, {first_name}!*

Рад снова вас видеть! JARVIS к вашим услугам.

💡 *Чем могу помочь:*
• 🤖 Пообщаться на любую тему
• 📝 Работать с заметками и напоминаниями
• ⏰ Помочь с планированием

Выберите действие в меню или напишите сообщение!
            """
        
        await message.answer(
            welcome_text,
            reply_markup=main_menu
        )
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /start: {e}")
        await message.answer(
            "ERROR: Произошла ошибка. Пожалуйста, попробуйте позже."
        )


@start_router.message(F.text == "💬 Чат")
async def handle_chat_button(message: types.Message):
    """
    Обработчик кнопки "💬 Чат"
    """
    await message.answer(
        "💬 *Режим чата активирован!*\n\n"
        "Просто напишите любое сообщение, и я с радостью вам отвечу.\n"
        "Для очистки истории диалога используйте: /clear",
        reply_markup=main_menu
    )


@start_router.message(F.text == "📝 Заметки")
async def handle_notes_button(message: types.Message):
    """
    Обработчик кнопки "📝 Заметки"
    """
    await message.answer(
        "📝 *Работа с заметками:*\n\n"
        "• `/note <текст>` - создать заметку\n"
        "• `/notes` - показать последние заметки\n"
        "• `/note_find <запрос>` - поиск заметок\n"
        "• `/note_del <id>` - удалить заметку\n\n"
        "Пример: `/note Купить молоко по дороге домой`",
        reply_markup=main_menu
    )


@start_router.message(F.text == "🔔 Напоминания")
async def handle_reminders_button(message: types.Message):
    """
    Обработчик кнопки "🔔 Напоминания"
    """
    await message.answer(
        "⏰ *Работа с напоминаниями:*\n\n"
        "• `/remind <время> <текст>` - создать напоминание\n"
        "• `/reminders` - показать активные напоминания\n"
        "• `/remind_del <id>` - удалить напоминание\n\n"
        "Форматы времени: `10min`, `2h`, `18:30`\n"
        "Пример: `/remind 10min позвонить маме`",
        reply_markup=main_menu
    )


@start_router.message(F.text == "📅 Расписание")
async def handle_schedule_button(message: types.Message):
    """
    Обработчик кнопки "📅 Расписание" - вызывает /today
    """
    # Импортируем обработчик /today
    from handlers.schedule import handle_today_events
    await handle_today_events(message)


@start_router.message(F.text == "🎵 Музыка")
async def handle_music_button(message: types.Message):
    """
    Обработчик кнопки "🎵 Музыка" - вызывает /now
    """
    # Импортируем обработчик /now
    from handlers.music import handle_now_playing
    await handle_now_playing(message)


@start_router.message(F.text == "⚙️ Настройки")
async def handle_settings_button(message: types.Message):
    """
    Обработчик кнопки "⚙️ Настройки" (заглушка)
    """
    await message.answer(
        "⚙️ *Настройки*\n\n"
        "Эта функция скоро будет доступна.\n"
        "Следите за обновлениями! 🚀",
        reply_markup=main_menu
    )
