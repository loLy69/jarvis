"""
Умный Spotify сервис - работает с любым VPN
"""
import os
import sys
import requests
import urllib3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import Config

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SmartSpotifyService:
    def __init__(self):
        self.scope = "user-read-playback-state user-read-currently-playing user-modify-playback-state"
        self.cache_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.spotify_cache')
        
    def get_client(self):
        """Получить клиент Spotify с автоматическим определением прокси"""
        try:
            # Создаем сессию
            session = requests.Session()
            session.verify = False
            
            # Пробуем разные варианты прокси
            proxy_options = [
                None,  # Без прокси
                {'http': 'http://127.0.0.1:1080', 'https': 'http://127.0.0.1:1080'},
                {'http': 'http://127.0.0.1:1087', 'https': 'http://127.0.0.1:1087'},
                {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'},
                {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'},
                {'http': 'socks5://127.0.0.1:1080', 'https': 'socks5://127.0.0.1:1080'},
                {'http': 'socks5://127.0.0.1:1087', 'https': 'socks5://127.0.0.1:1087'},
            ]
            
            for proxy in proxy_options:
                try:
                    if proxy:
                        session.proxies.update(proxy)
                        print(f"Пробуем прокси: {proxy}")
                    else:
                        print("Пробуем без прокси")
                    
                    # Создаем клиент с текущими настройками
                    sp = spotipy.Spotify(
                        auth_manager=SpotifyOAuth(
                            client_id=Config.SPOTIFY_CLIENT_ID,
                            client_secret=Config.SPOTIFY_CLIENT_SECRET,
                            redirect_uri=Config.SPOTIFY_REDIRECT_URI,
                            scope=self.scope,
                            cache_path=self.cache_path
                        ),
                        requests_session=session
                    )
                    
                    # Быстрая проверка соединения
                    user = sp.current_user()
                    print(f"✅ Успешное подключение! Пользователь: {user['display_name']}")
                    return sp
                    
                except Exception as e:
                    print(f"❌ Не удалось: {e}")
                    continue
            
            print("❌ Все варианты подключения не сработали")
            return None
            
        except Exception as e:
            print(f"ERROR: {e}")
            return None
    
    def get_current_track(self):
        """Получить текущий трек"""
        try:
            sp = self.get_client()
            if not sp:
                return None
                
            current = sp.current_playback()
            if current and current.get('item'):
                track = current['item']
                return {
                    'artist': track['artists'][0]['name'],
                    'track': track['name'],
                    'album': track['album']['name'],
                    'is_playing': current['is_playing']
                }
            return None
        except Exception as e:
            print(f"ERROR: {e}")
            return None
    
    def pause_playback(self):
        """Пауза"""
        try:
            sp = self.get_client()
            if sp:
                sp.pause_playback()
                return True
        except Exception as e:
            print(f"ERROR: {e}")
        return False
    
    def resume_playback(self):
        """Возобновить"""
        try:
            sp = self.get_client()
            if sp:
                sp.start_playback()
                return True
        except Exception as e:
            print(f"ERROR: {e}")
        return False
    
    def next_track(self):
        """Следующий трек"""
        try:
            sp = self.get_client()
            if sp:
                sp.next_track()
                return True
        except Exception as e:
            print(f"ERROR: {e}")
        return False
    
    def previous_track(self):
        """Предыдущий трек"""
        try:
            sp = self.get_client()
            if sp:
                sp.previous_track()
                return True
        except Exception as e:
            print(f"ERROR: {e}")
        return False

# Глобальный экземпляр
smart_spotify_service = SmartSpotifyService()
