"""
Настройка Spotify для JARVIS
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import sys

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

print("Настройка Spotify для JARVIS")
print("=" * 40)

# Проверяем настройки
required_vars = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'SPOTIFY_REDIRECT_URI']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print("Отсутствуют переменные в .env:")
    for var in missing_vars:
        print(f"   • {var}")
    print("\nДобавьте их в .env файл:")
    print("SPOTIFY_CLIENT_ID=ваш_client_id")
    print("SPOTIFY_CLIENT_SECRET=ваш_client_secret") 
    print("SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback")
    exit(1)

print("Переменные окружения найдены")

# Авторизация
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="user-read-playback-state user-read-currently-playing user-modify-playback-state",
        cache_path=".spotify_cache"
    ))

    user = sp.current_user()
    print(f"Авторизация успешна!")
    print(f"Пользователь: {user['display_name']}")
    print(f"Email: {user.get('email', 'не указан')}")
    print(f"Страна: {user.get('country', 'не указана')}")
    print(f"Тип аккаунта: {user.get('product', 'unknown')}")
    
    # Проверяем устройства
    devices = sp.devices()
    print(f"\nНайдено устройств: {len(devices.get('devices', []))}")
    
    for device in devices.get('devices', []):
        status = "Активен" if device['is_active'] else "Неактивен"
        print(f"   {status} {device['name']} ({device['type']})")
    
    print(f"\nГотово! Теперь можно использовать команды:")
    print(f"   • /now - что сейчас играет")
    print(f"   • /pause - пауза/возобновление")
    print(f"   • /next - следующий трек")
    print(f"   • /prev - предыдущий трек")
    
except Exception as e:
    print(f"Ошибка: {e}")
    print("\nВозможные решения:")
    print("1. Проверьте SPOTIFY_CLIENT_ID и SPOTIFY_CLIENT_SECRET")
    print("2. Убедитесь что REDIRECT_URI = http://127.0.0.1:8888/callback")
    print("3. Удалите .spotify_cache и попробуйте снова")
