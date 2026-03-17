"""
Тестовый скрипт для проверки Spotify авторизации
"""
import os
from config import Config
from services.spotify_client import spotify_client

def main():
    print("=== Тест Spotify ===")
    print(f"Client ID: {Config.SPOTIFY_CLIENT_ID}")
    print(f"Client Secret: {Config.SPOTIFY_CLIENT_SECRET}")
    print(f"Redirect URI: {Config.SPOTIFY_REDIRECT_URI}")
    
    # Проверяем наличие переменных
    if not all([Config.SPOTIFY_CLIENT_ID, Config.SPOTIFY_CLIENT_SECRET, Config.SPOTIFY_REDIRECT_URI]):
        print("ERROR: Отсутствуют переменные окружения для Spotify")
        return
    
    # Пробуем получить клиент
    print("Попытка авторизации в Spotify...")
    try:
        sp = spotify_client.get_spotify_client()
        if sp:
            print("✅ Spotify клиент успешно создан")
            
            # Проверяем текущий трек
            import asyncio
            async def test_current_track():
                track_info = await spotify_client.get_current_track()
                if track_info:
                    print(f"Сейчас играет: {track_info['artist']} — {track_info['track']}")
                else:
                    print("Сейчас ничего не играет или нет активного устройства")
            
            asyncio.run(test_current_track())
        else:
            print("❌ Не удалось создать Spotify клиент")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
