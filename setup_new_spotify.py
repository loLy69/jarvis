"""
Новая настройка Spotify с нуля
"""
import sys
import os
from spotify_new import spotify_new

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

print("Новая настройка Spotify")
print("=" * 30)

# Проверяем переменные
required = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'SPOTIFY_REDIRECT_URI']
missing = [var for var in required if not os.getenv(var)]

if missing:
    print("Отсутствуют переменные:")
    for var in missing:
        print(f"  • {var}")
    print("\nДобавьте в .env:")
    print("SPOTIFY_CLIENT_ID=...")
    print("SPOTIFY_CLIENT_SECRET=...")
    print("SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback")
    exit(1)

# Тестируем подключение
try:
    sp = spotify_new.get_spotify()
    if sp:
        print("✅ Подключение успешно!")
        
        # Текущий трек
        track = spotify_new.get_now_playing()
        if track:
            print(f"🎵 Играет: {track['artist']} - {track['track']}")
        else:
            print("🎵 Ничего не играет")
            
        # Устройства
        devices = sp.devices()
        print(f"📱 Устройств: {len(devices.get('devices', []))}")
        for device in devices.get('devices', []):
            status = "🟢" if device['is_active'] else "⚪"
            print(f"   {status} {device['name']} ({device['type']})")
    else:
        print("❌ Ошибка подключения")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
    
print("\nГотово! Используйте команды:")
print("  /now - что играет")
print("  /pause - пауза/воспроизведение")
print("  /next - следующий трек")
print("  /prev - предыдущий трек")
