"""
Полностью новая система Spotify с нуля
"""
import os
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

class NewSpotify:
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
        self.cache_file = ".spotify_cache"
        
    def get_spotify(self):
        """Получить клиент Spotify"""
        try:
            # Создаем OAuth менеджер
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope="user-read-playback-state user-read-currently-playing user-modify-playback-state",
                cache_path=self.cache_file
            )
            
            # Создаем клиент
            sp = spotipy.Spotify(auth_manager=auth_manager)
            
            # Проверяем подключение
            user = sp.current_user()
            print(f"Подключено к Spotify: {user['display_name']}")
            return sp
            
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return None
    
    def get_now_playing(self):
        """Получить текущий трек"""
        try:
            sp = self.get_spotify()
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
            print(f"Ошибка получения трека: {e}")
            return None
    
    def pause(self):
        """Пауза"""
        try:
            sp = self.get_spotify()
            if sp:
                sp.pause_playback()
                return True
        except Exception as e:
            print(f"Ошибка паузы: {e}")
        return False
    
    def play(self):
        """Воспроизведение"""
        try:
            sp = self.get_spotify()
            if sp:
                sp.start_playback()
                return True
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")
        return False
    
    def next_track(self):
        """Следующий трек"""
        try:
            sp = self.get_spotify()
            if sp:
                sp.next_track()
                return True
        except Exception as e:
            print(f"Ошибка переключения: {e}")
        return False
    
    def prev_track(self):
        """Предыдущий трек"""
        try:
            sp = self.get_spotify()
            if sp:
                sp.previous_track()
                return True
        except Exception as e:
            print(f"Ошибка переключения: {e}")
        return False
    
    def search_and_play(self, query: str):
        """Найти и включить плейлист"""
        try:
            sp = self.get_spotify()
            if not sp:
                return None
                
            # Ищем плейлисты
            results = sp.search(q=query, type='playlist', limit=5)
            
            if not results['playlists']['items']:
                return None
                
            # Берем первый найденный плейлист
            playlist = results['playlists']['items'][0]
            playlist_uri = playlist['uri']
            playlist_name = playlist['name']
            
            # Включаем плейлист
            sp.start_playback(context_uri=playlist_uri)
            
            return playlist_name
            
        except Exception as e:
            print(f"Ошибка поиска плейлиста: {e}")
            return None

# Глобальный экземпляр
spotify_new = NewSpotify()
