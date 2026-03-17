"""
Сервис для работы с Google Calendar API
"""
import base64
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import Config


class GoogleCalendarService:
    """Класс для работы с Google Calendar API"""
    
    def __init__(self):
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        self.token_file = 'token.json'
    
    def get_calendar_service(self):
        """
        Авторизует и возвращает сервис Google Calendar
        
        Returns:
            Объект сервиса Google Calendar или None в случае ошибки
        """
        try:
            creds = None
            
            # Проверяем наличие сохраненного токена
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            
            # Если токен отсутствует или просрочен
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # Декодируем credentials из base64
                    if not Config.GOOGLE_CREDENTIALS:
                        print("ERROR: GOOGLE_CREDENTIALS не найдены в переменных окружения")
                        return None
                    
                    try:
                        credentials_json = base64.b64decode(Config.GOOGLE_CREDENTIALS).decode('utf-8')
                        credentials_dict = json.loads(credentials_json)
                    except Exception as e:
                        print(f"ERROR: Ошибка декодирования GOOGLE_CREDENTIALS: {e}")
                        return None
                    
                    flow = InstalledAppFlow.from_client_config(
                        credentials_dict, 
                        self.scopes
                    )
                    creds = flow.run_local_server(port=0)
                
                # Сохраняем токен
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            
            # Создаем сервис
            self.service = build('calendar', 'v3', credentials=creds)
            return self.service
            
        except Exception as e:
            print(f"ERROR: Ошибка создания сервиса Google Calendar: {e}")
            return None
    
    async def get_today_events(self) -> List[Dict]:
        """
        Получает события на сегодня
        
        Returns:
            Список событий на сегодня
        """
        if not self.service:
            self.get_calendar_service()
        
        if not self.service:
            return []
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' означает UTC
            end_of_day = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end_of_day,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Форматируем события
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Парсим время
                if 'T' in start:
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    time_str = start_dt.strftime('%H:%M')
                else:
                    time_str = 'Весь день'
                
                formatted_events.append({
                    'time': time_str,
                    'title': event['summary'],
                    'description': event.get('description', ''),
                    'start': start,
                    'end': end
                })
            
            return formatted_events
            
        except HttpError as e:
            print(f"ERROR: Ошибка API Google Calendar: {e}")
            return []
        except Exception as e:
            print(f"ERROR: Ошибка получения событий на сегодня: {e}")
            return []
    
    async def get_week_events(self) -> Dict[str, List[Dict]]:
        """
        Получает события на ближайшие 7 дней
        
        Returns:
            Словарь с событиями, сгруппированными по дням
        """
        if not self.service:
            self.get_calendar_service()
        
        if not self.service:
            return {}
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            end_of_week = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end_of_week,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Группируем по дням
            week_events = {}
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                
                # Получаем дату
                if 'T' in start:
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    date_str = start_dt.strftime('%d.%m.%Y')
                    date_day = start_dt.strftime('%d.%m')
                    day_name = start_dt.strftime('%A')
                else:
                    date_str = start
                    date_day = start
                    day_name = 'Весь день'
                
                # Время
                time_str = start_dt.strftime('%H:%M') if 'T' in start else 'Весь день'
                
                # Добавляем в группу
                if date_str not in week_events:
                    week_events[date_str] = {
                        'day': date_day,
                        'day_name': day_name,
                        'events': []
                    }
                
                week_events[date_str]['events'].append({
                    'time': time_str,
                    'title': event['summary'],
                    'description': event.get('description', '')
                })
            
            return week_events
            
        except HttpError as e:
            print(f"ERROR: Ошибка API Google Calendar: {e}")
            return {}
        except Exception as e:
            print(f"ERROR: Ошибка получения событий на неделю: {e}")
            return {}
    
    async def create_event(self, date_str: str, time_str: str, title: str, duration_hours: int = 1) -> bool:
        """
        Создает новое событие в календаре
        
        Args:
            date_str: Дата в формате DD.MM или DD.MM.YYYY
            time_str: Время в формате HH:MM
            title: Название события
            duration_hours: Длительность в часах
            
        Returns:
            True если событие создано, иначе False
        """
        if not self.service:
            self.get_calendar_service()
        
        if not self.service:
            return False
        
        try:
            # Парсим дату
            if len(date_str) == 5:  # DD.MM
                year = datetime.now().year
                date_obj = datetime.strptime(f"{date_str}.{year}", "%d.%m.%Y")
            else:  # DD.MM.YYYY
                date_obj = datetime.strptime(date_str, "%d.%m.%Y")
            
            # Парсим время
            time_obj = datetime.strptime(time_str, "%H:%M")
            
            # Создаем datetime начала события
            start_datetime = datetime.combine(
                date_obj.date(), 
                time_obj.time()
            )
            
            # Конец события
            end_datetime = start_datetime + timedelta(hours=duration_hours)
            
            # Форматируем для API
            start_iso = start_datetime.isoformat() + 'Z'
            end_iso = end_datetime.isoformat() + 'Z'
            
            # Создаем событие
            event = {
                'summary': title,
                'start': {
                    'dateTime': start_iso,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_iso,
                    'timeZone': 'UTC',
                },
            }
            
            event_result = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            print(f"OK: Событие создано: {event_result.get('htmlLink')}")
            return True
            
        except HttpError as e:
            print(f"ERROR: Ошибка создания события: {e}")
            return False
        except Exception as e:
            print(f"ERROR: Ошибка парсинга даты/времени: {e}")
            return False


# Глобальный экземпляр сервиса
calendar_service = GoogleCalendarService()
