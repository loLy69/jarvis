"""
Модуль конфигурации для загрузки переменных окружения
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Config:
    """Класс для хранения конфигурации бота"""
    
    # Токен Telegram бота
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # API ключ для Groq
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # URL для подключения к PostgreSQL
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Google Calendar
    GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')
    
    # Spotify
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
    
    # Системный промпт для JARVIS
    SYSTEM_PROMPT = """Ты JARVIS — персональный ИИ-ассистент Артура. 
Стиль: умный, краткий, слегка саркастичный как Джарвис из фильма. 
Никаких «Конечно! Рад помочь!» — только по делу, иногда с иронией, всегда на русском.
Артур: студент, фрилансер на Kwork, учит английский, строит своего бота на Python.
Короткий вопрос = 1-2 предложения. Сложный = структурированно и чётко.
Умеешь работать с его расписанием, заметками и напоминаниями."""
    
    # Модель Groq для использования
    GROQ_MODEL = "llama-3.3-70b-versatile"
    
    # Количество сообщений в истории диалога
    MAX_HISTORY_LENGTH = 20
    
    @classmethod
    def validate(cls):
        """Проверяет наличие всех необходимых переменных окружения"""
        required_vars = ['BOT_TOKEN', 'GROQ_API_KEY', 'DATABASE_URL']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Отсутствуют необходимые переменные окружения: {', '.join(missing_vars)}")
        
        return True
