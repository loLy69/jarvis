"""
Сервис для работы с Spotify API
"""
import os
import ssl
from typing import Dict, List, Optional, Tuple

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

from config import Config


class SpotifyClient:
    """Класс для работы с Spotify API"""
    
    def __init__(self):
        self.sp = None
        self.scope = [
            'user-read-playback-state',
            'user-modify-playback-state',
            'user-read-currently-playing',
            'playlist-read-private'
        ]
        # Абсолютный путь к .spotify_cache в корне проекта
        project_root = os.path.dirname(os.path.dirname(__file__))  # jarvs/
        self.cache_path = os.path.join(project_root, '.spotify_cache')
        print(f"DEBUG: Spotify cache path: {self.cache_path}")
        
        # Проверяем наличие необходимых переменных
        if not all([Config.SPOTIFY_CLIENT_ID, Config.SPOTIFY_CLIENT_SECRET, Config.SPOTIFY_REDIRECT_URI]):
            print("ERROR: Отсутствуют переменные для Spotify (CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)")
            return
        
        # Инициализируем OAuth
        self.sp_oauth = SpotifyOAuth(
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET,
            redirect_uri=Config.SPOTIFY_REDIRECT_URI,
            scope=self.scope,
            cache_path=self.cache_path
        )
    
    def get_spotify_client(self):
        """
        Авторизует и возвращает клиент Spotify
        
        Returns:
            Объект клиента Spotify или None в случае ошибки
        """
        try:
            # Пробуем получить токен из кэша
            token_info = self.sp_oauth.get_cached_token()
            
            if not token_info:
                print("INFO: Токен Spotify не найден. Пройдите авторизацию: python spotify_auth.py")
                return None
            
            # Проверяем не истек ли токен и обновляем если нужно
            if self.sp_oauth.is_token_expired(token_info):
                print("INFO: Токен Spotify истек, обновляю...")
                token_info = self.sp_oauth.refresh_access_token(token_info['refresh_token'])
                print("OK: Токен обновлен")
            
            # Создаем клиент (как было в рабочей версии)
            self.sp = spotipy.Spotify(auth=token_info['access_token'])
            return self.sp
            
        except Exception as e:
            print(f"ERROR: Ошибка создания клиента Spotify: {e}")
            return None
    
    async def get_current_track(self) -> Optional[Dict]:
        """
        Получает информацию о текущем треке
        
        Returns:
            Словарь с информацией о треке или None если ничего не играет
        """
        try:
            sp = self.get_spotify_client()
            if not sp:
                return None
            
            # Получаем текущий трек
            current = sp.current_playback()
            
            if not current or not current.get('item'):
                return None
            
            track = current['item']
            artist = track['artists'][0]['name'] if track['artists'] else 'Unknown Artist'
            track_name = track['name']
            album = track['album']['name']
            
            # Получаем прогресс и длительность
            progress_ms = current.get('progress_ms', 0)
            duration_ms = track['duration_ms']
            
            # Получаем информацию об устройстве
            device = current.get('device', {})
            device_name = device.get('name', 'Unknown Device')
            device_type = device.get('type', 'Unknown')
            
            return {
                'track': track_name,
                'artist': artist,
                'album': album,
                'progress': progress_ms,
                'duration': duration_ms,
                'device': device_name,
                'device_type': device_type,
                'is_playing': current.get('is_playing', False)
            }
            
        except SpotifyException as e:
            print(f"ERROR: Ошибка API Spotify: {e}")
            return None
        except Exception as e:
            print(f"ERROR: Ошибка получения текущего трека: {e}")
            return None
    
    async def toggle_playback(self) -> bool:
        """
        Переключает воспроизведение (пауза/возобновление)
        
        Returns:
            True если операция успешна
        """
        if not self.sp:
            self.get_spotify_client()
        
        if not self.sp:
            return False
        
        try:
            current = self.sp.current_playback()
            
            if current and current['is_playing']:
                self.sp.pause_playback()
                print("OK: Воспроизведение приостановлено")
            else:
                self.sp.start_playback()
                print("OK: Воспроизведение возобновлено")
            
            return True
            
        except SpotifyException as e:
            if "NO_ACTIVE_DEVICE" in str(e):
                print("ERROR: Нет активного устройства Spotify")
                return False
            print(f"ERROR: Ошибка переключения воспроизведения: {e}")
            return False
        except Exception as e:
            print(f"ERROR: Ошибка toggle playback: {e}")
            return False
    
    async def next_track(self) -> bool:
        """
        Переключает на следующий трек
        
        Returns:
            True если операция успешна
        """
        if not self.sp:
            self.get_spotify_client()
        
        if not self.sp:
            return False
        
        try:
            self.sp.next_track()
            print("OK: Переключено на следующий трек")
            return True
            
        except SpotifyException as e:
            if "NO_ACTIVE_DEVICE" in str(e):
                print("ERROR: Нет активного устройства Spotify")
                return False
            print(f"ERROR: Ошибка следующего трека: {e}")
            return False
        except Exception as e:
            print(f"ERROR: Ошибка next track: {e}")
            return False
    
    async def previous_track(self) -> bool:
        """
        Переключает на предыдущий трек
        
        Returns:
            True если операция успешна
        """
        if not self.sp:
            self.get_spotify_client()
        
        if not self.sp:
            return False
        
        try:
            self.sp.previous_track()
            print("OK: Переключено на предыдущий трек")
            return True
            
        except SpotifyException as e:
            if "NO_ACTIVE_DEVICE" in str(e):
                print("ERROR: Нет активного устройства Spotify")
                return False
            print(f"ERROR: Ошибка предыдущего трека: {e}")
            return False
        except Exception as e:
            print(f"ERROR: Ошибка previous track: {e}")
            return False
    
    async def set_volume(self, volume_percent: int) -> bool:
        """
        Устанавливает громкость
        
        Args:
            volume_percent: Громкость от 0 до 100
            
        Returns:
            True если операция успешна
        """
        if not 0 <= volume_percent <= 100:
            print("ERROR: Громкость должна быть от 0 до 100")
            return False
        
        if not self.sp:
            self.get_spotify_client()
        
        if not self.sp:
            return False
        
        try:
            self.sp.volume(volume_percent)
            print(f"OK: Громкость установлена на {volume_percent}%")
            return True
            
        except SpotifyException as e:
            if "NO_ACTIVE_DEVICE" in str(e):
                print("ERROR: Нет активного устройства Spotify")
                return False
            print(f"ERROR: Ошибка установки громкости: {e}")
            return False
        except Exception as e:
            print(f"ERROR: Ошибка set volume: {e}")
            return False
    
    async def get_user_playlists(self, limit: int = 10) -> List[Dict]:
        """
        Получает плейлисты пользователя
        
        Args:
            limit: Количество плейлистов
            
        Returns:
            Список плейлистов
        """
        if not self.sp:
            self.get_spotify_client()
        
        if not self.sp:
            return []
        
        try:
            playlists = self.sp.current_user_playlists(limit=limit)
            
            formatted_playlists = []
            for i, playlist in enumerate(playlists['items'], 1):
                formatted_playlists.append({
                    'number': i,
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'tracks_count': playlist['tracks']['total']
                })
            
            return formatted_playlists
            
        except SpotifyException as e:
            print(f"ERROR: Ошибка получения плейлистов: {e}")
            return []
        except Exception as e:
            print(f"ERROR: Ошибка get playlists: {e}")
            return []
    
    async def play_playlist(self, playlist_number: int) -> bool:
        """
        Включает плейлист по номеру
        
        Args:
            playlist_number: Номер плейлиста из списка
            
        Returns:
            True если операция успешна
        """
        playlists = await self.get_user_playlists()
        
        # Ищем плейлист по номеру
        target_playlist = None
        for playlist in playlists:
            if playlist['number'] == playlist_number:
                target_playlist = playlist
                break
        
        if not target_playlist:
            print(f"ERROR: Плейлист с номером {playlist_number} не найден")
            return False
        
        if not self.sp:
            self.get_spotify_client()
        
        if not self.sp:
            return False
        
        try:
            self.sp.start_playback(context_uri=f"spotify:playlist:{target_playlist['id']}")
            print(f"OK: Включен плейлист: {target_playlist['name']}")
            return True
            
        except SpotifyException as e:
            if "NO_ACTIVE_DEVICE" in str(e):
                print("ERROR: Нет активного устройства Spotify")
                return False
            print(f"ERROR: Ошибка воспроизведения плейлиста: {e}")
            return False
        except Exception as e:
            print(f"ERROR: Ошибка play playlist: {e}")
            return False
    
    def _ms_to_time(self, ms: int) -> str:
        """
        Конвертирует миллисекунды в формат MM:SS
        
        Args:
            ms: Миллисекунды
            
        Returns:
            Время в формате MM:SS
        """
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"


# Глобальный экземпляр клиента
spotify_client = SpotifyClient()
