"""
Новые обработчики Spotify с нуля
"""
from aiogram import Router, types
from aiogram.filters import Command
from spotify_new import spotify_new

spotify_new_router = Router()

@spotify_new_router.message(Command("now"))
async def handle_now(message: types.Message):
    """Что сейчас играет"""
    try:
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

@spotify_new_router.message(Command("pause"))
async def handle_pause(message: types.Message):
    """Пауза/воспроизведение"""
    try:
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

@spotify_new_router.message(Command("next"))
async def handle_next(message: types.Message):
    """Следующий трек"""
    try:
        if spotify_new.next_track():
            await message.answer("⏭️ Следующий трек")
        else:
            await message.answer("❌ Не удалось переключить")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@spotify_new_router.message(Command("prev"))
async def handle_prev(message: types.Message):
    """Предыдущий трек"""
    try:
        if spotify_new.prev_track():
            await message.answer("⏮️ Предыдущий трек")
        else:
            await message.answer("❌ Не удалось переключить")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
