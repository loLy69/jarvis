"""
Простой сервис для работы с Spotify
"""
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import Config

class SpotifyService:
    def __init__(self):
        self.scope = "user-read-playback-state user-read-currently-playing user-modify-playback-state"
        self.cache_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.spotify_cache')
        
        # Настройки прокси
        self.proxy = None
        if os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY'):
            self.proxy = {
                'http': os.getenv('HTTP_PROXY'),
                'https': os.getenv('HTTPS_PROXY')
            }
            print(f"Используем прокси: {self.proxy}")
        
    def get_client(self):
        """Получить клиент Spotify"""
        try:
            # Если есть прокси, настраиваем requests
            if self.proxy:
                import requests
                import urllib3
                
                # Создаем сессию с прокси
                session = requests.Session()
                session.proxies.update(self.proxy)
                session.verify = False  # Отключаем проверку SSL для прокси
                
                # Отключаем предупреждения
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                
                return spotipy.Spotify(
                    auth_manager=SpotifyOAuth(
                        client_id=Config.SPOTIFY_CLIENT_ID,
                        client_secret=Config.SPOTIFY_CLIENT_SECRET,
                        redirect_uri=Config.SPOTIFY_REDIRECT_URI,
                        scope=self.scope,
                        cache_path=self.cache_path
                    ),
                    requests_session=session
                )
            else:
                return spotipy.Spotify(auth_manager=SpotifyOAuth(
                    client_id=Config.SPOTIFY_CLIENT_ID,
                    client_secret=Config.SPOTIFY_CLIENT_SECRET,
                    redirect_uri=Config.SPOTIFY_REDIRECT_URI,
                    scope=self.scope,
                    cache_path=self.cache_path
                ))
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
spotify_service = SpotifyService()
