"""
Обработчики для работы с Spotify
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from services.spotify_client import spotify_client

# Создаем роутер для обработчиков музыки
music_router = Router()

@music_router.message(Command("test_music"))
async def handle_test_music(message: types.Message):
    """Тестовая команда для музыки"""
    await message.answer("✅ Музыка работает!")


@music_router.message(Command("now"))
async def handle_now_playing(message: types.Message):
    """
    Обработчик команды /now - что сейчас играет
    """
    try:
        # Получаем информацию о текущем треке
        track_info = await spotify_client.get_current_track()
        
        if not track_info:
            await message.answer("🎵 Сейчас ничего не играет.")
            return
        
        # Формируем ответ
        response = (
            f"🎵 *Сейчас играет:*\n"
            f"{track_info['artist']} — {track_info['track']}\n\n"
            f"{track_info['progress_bar']}\n"
            f"{track_info['current_time']} / {track_info['total_time']}"
        )
        
        await message.answer(response)
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /now: {e}")
        await message.answer(
            "🎵 Spotify не активен. Открой приложение на любом устройстве."
        )


@music_router.message(Command("pause"))
async def handle_pause_playback(message: types.Message):
    """
    Обработчик команды /pause - пауза/возобновление
    """
    try:
        success = await spotify_client.toggle_playback()
        
        if success:
            await message.answer("⏯️ Воспроизведение переключено.")
        else:
            await message.answer(
                "🎵 Spotify не активен. Открой приложение на любом устройстве."
            )
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /pause: {e}")
        await message.answer(
            "ERROR: Не удалось переключить воспроизведение. Попробуйте еще раз."
        )


@music_router.message(Command("next"))
async def handle_next_track(message: types.Message):
    """
    Обработчик команды /next - следующий трек
    """
    try:
        success = await spotify_client.next_track()
        
        if success:
            await message.answer("⏭️ Переключено на следующий трек.")
        else:
            await message.answer(
                "🎵 Spotify не активен. Открой приложение на любом устройстве."
            )
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /next: {e}")
        await message.answer(
            "ERROR: Не удалось переключить трек. Попробуйте еще раз."
        )


@music_router.message(Command("prev"))
async def handle_previous_track(message: types.Message):
    """
    Обработчик команды /prev - предыдущий трек
    """
    try:
        success = await spotify_client.previous_track()
        
        if success:
            await message.answer("⏮️ Переключено на предыдущий трек.")
        else:
            await message.answer(
                "🎵 Spotify не активен. Открой приложение на любом устройстве."
            )
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /prev: {e}")
        await message.answer(
            "ERROR: Не удалось переключить трек. Попробуйте еще раз."
        )


@music_router.message(Command("volume"))
async def handle_set_volume(message: types.Message):
    """
    Обработчик команды /volume - установить громкость
    """
    text = message.text
    
    # Получаем громкость
    parts = text.replace('/volume', '').strip().split()
    
    if not parts or not parts[0].isdigit():
        await message.answer(
            "🔊 Использование: /volume <0-100>\n"
            "Пример: /volume 50\n\n"
            "Устанавливает громкость от 0 до 100%."
        )
        return
    
    volume = int(parts[0])
    
    if not 0 <= volume <= 100:
        await message.answer("❌ Громкость должна быть от 0 до 100.")
        return
    
    try:
        success = await spotify_client.set_volume(volume)
        
        if success:
            await message.answer(f"🔊 Громкость установлена на {volume}%.")
        else:
            await message.answer(
                "🎵 Spotify не активен. Открой приложение на любом устройстве."
            )
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /volume: {e}")
        await message.answer(
            "ERROR: Не удалось установить громкость. Попробуйте еще раз."
        )


@music_router.message(Command("playlists"))
async def handle_show_playlists(message: types.Message):
    """
    Обработчик команды /playlists - показать плейлисты
    """
    try:
        playlists = await spotify_client.get_user_playlists(10)
        
        if not playlists:
            await message.answer("📋 У вас нет плейлистов.")
            return
        
        # Формируем ответ
        response = "📋 *Ваши плейлисты:*\n\n"
        
        for playlist in playlists:
            response += (
                f"*{playlist['number']}.* {playlist['name']}\n"
                f"   🎵 {playlist['tracks_count']} треков\n\n"
            )
        
        response += "💡 Для воспроизведения: /play <номер>"
        
        await message.answer(response)
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /playlists: {e}")
        await message.answer(
            "ERROR: Не удалось загрузить плейлисты. Попробуйте еще раз."
        )


@music_router.message(Command("play"))
async def handle_play_playlist(message: types.Message):
    """
    Обработчик команды /play - включить плейлист
    """
    text = message.text
    
    # Получаем номер плейлиста
    parts = text.replace('/play', '').strip().split()
    
    if not parts or not parts[0].isdigit():
        await message.answer(
            "🎵 Использование: /play <номер>\n"
            "Пример: /play 3\n\n"
            "💡 Номер плейлиста можно посмотреть в /playlists"
        )
        return
    
    playlist_number = int(parts[0])
    
    try:
        success = await spotify_client.play_playlist(playlist_number)
        
        if success:
            await message.answer(f"🎵 Включен плейлист #{playlist_number}.")
        else:
            await message.answer(
                "🎵 Spotify не активен или плейлист не найден. "
                "Открой приложение на любом устройстве."
            )
        
    except Exception as e:
        print(f"ERROR: Ошибка в обработчике /play: {e}")
        await message.answer(
            "ERROR: Не удалось включить плейлист. Попробуйте еще раз."
        )
