import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

print("Тест API Spotify...")

try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private",
        cache_path=".spotify_cache"
    ))
    
    print("1. Проверяем текущий пользователь...")
    user = sp.current_user()
    print(f"   Пользователь: {user['display_name']}")
    
    print("2. Проверяем устройства...")
    devices = sp.devices()
    print(f"   Найдено устройств: {len(devices.get('devices', []))}")
    
    for device in devices.get('devices', []):
        status = "Активен" if device['is_active'] else "Неактивен"
        print(f"   - {device['name']} ({device['type']}) - {status}")
    
    print("3. Проверяем текущий трек...")
    current = sp.current_playback()
    if current and current.get('item'):
        track = current['item']
        print(f"   Играет: {track['artists'][0]['name']} - {track['name']}")
    else:
        print("   Ничего не играет")
        
except Exception as e:
    print(f"ОШИБКА: {e}")
