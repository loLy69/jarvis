"""
Обработчики для авторизации сервисов
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from services.spotify_client import spotify_client

# Создаем роутер для обработчиков авторизации
auth_router = Router()


@auth_router.message(Command("test"))
async def handle_test(message: types.Message):
    """Тестовая команда"""
    await message.answer("✅ Тест работает! Бот отвечает на команды.")


@auth_router.message(Command("spotify_auth"))
async def handle_spotify_auth(message: types.Message):
    """
    Обработчик команды /spotify_auth - авторизация Spotify
    """
    try:
        # Проверяем наличие настроек
        from config import Config
        if not all([Config.SPOTIFY_CLIENT_ID, Config.SPOTIFY_CLIENT_SECRET, Config.SPOTIFY_REDIRECT_URI]):
            await message.answer(
                "❌ Отсутствуют настройки Spotify. Добавьте переменные в .env:\n"
                "• SPOTIFY_CLIENT_ID\n"
                "• SPOTIFY_CLIENT_SECRET\n"
                "• SPOTIFY_REDIRECT_URI"
            )
            return
        
        # Получаем URL для авторизации
        if not hasattr(spotify_client, 'sp_oauth') or not spotify_client.sp_oauth:
            await message.answer("❌ Клиент Spotify не инициализирован")
            return
        
        auth_url = spotify_client.sp_oauth.get_authorize_url()
        
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
        print(f"ERROR: Ошибка в обработчике /spotify_auth: {e}")
        await message.answer("❌ Ошибка при генерации ссылки авторизации")


@auth_router.message(Command("spotify_code"))
async def handle_spotify_code(message: types.Message):
    """
    Обработчик команды /spotify_code - ввод кода авторизации
    """
    text = message.text
    
    # Получаем код
    parts = text.replace('/spotify_code', '').strip().split()
    
    if not parts:
        await message.answer(
            "❌ Использование: `/spotify_code <код>`\n\n"
            "Пример: `/spotify_code AQD...xyz123`"
        )
        return
    
    code = parts[0]
    
    try:
        # Обмениваем код на токен
        token_info = spotify_client.sp_oauth.get_access_token(code)
        
        if token_info:
            await message.answer(
                "✅ Spotify успешно авторизован!\n\n"
                "Теперь можно использовать команды:\n"
                "• /now - что играет\n"
                "• /pause - пауза/воспроизведение\n"
                "• /next - следующий трек\n"
                "• /playlists - плейлисты"
            )
            print("OK: Spotify авторизован")
        else:
            await message.answer("❌ Не удалось получить токен. Проверьте код.")
        
    except Exception as e:
        print(f"ERROR: Ошибка авторизации Spotify: {e}")
        await message.answer("❌ Ошибка при авторизации. Попробуйте еще раз.")
