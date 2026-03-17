import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import sys

# Устанавливаем кодировку для Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

# Проверяем наличие переменных
if not all([os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"), os.getenv("SPOTIFY_REDIRECT_URI")]):
    print("ERROR: Отсутствуют переменные окружения для Spotify")
    print("Добавьте в .env:")
    print("SPOTIFY_CLIENT_ID=...")
    print("SPOTIFY_CLIENT_SECRET=...")
    print("SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback")
    exit(1)

print("Запускаем авторизацию Spotify...")
print("Откроется браузер для авторизации")

try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private",
        cache_path=".spotify_cache"
    ))

    # Проверяем авторизацию
    user = sp.current_user()
    print(f"Авторизация успешна!")
    print(f"Пользователь: {user['display_name']}")
    print(f"Email: {user.get('email', 'не указан')}")
    print(f"Токен сохранен в .spotify_cache")
    print(f"\nТеперь можно использовать команды в боте:")
    print(f"• /now - что сейчас играет")
    print(f"• /pause - пауза/воспроизведение")
    print(f"• /next - следующий трек")
    
except Exception as e:
    print(f"Ошибка авторизации: {e}")
    print("\nВозможные решения:")
    print("1. Проверьте SPOTIFY_CLIENT_ID и SPOTIFY_CLIENT_SECRET")
    print("2. Убедитесь что REDIRECT_URI = http://127.0.0.1:8888/callback")
    print("3. Удалите файл .spotify_cache и попробуйте снова")
