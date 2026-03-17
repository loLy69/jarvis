"""
Модуль для работы с базой данных SQLite
"""
import aiosqlite
from typing import Optional
from config import Config


class Database:
    """Класс для управления подключением к базе данных"""
    
    def __init__(self):
        self.db_path = Config.DATABASE_URL.replace("sqlite:///", "")
    
    async def connect(self):
        """Создает подключение к базе данных"""
        try:
            # SQLite не требует отдельного подключения, файл создается автоматически
            print("OK: Подключение к базе данных установлено")
        except Exception as e:
            print(f"ERROR: Ошибка подключения к базе данных: {e}")
            raise
    
    async def disconnect(self):
        """Закрывает подключение к базе данных"""
        print("CLOSE: Подключение к базе данных закрыто")
    
    async def create_tables(self):
        """Создает необходимые таблицы в базе данных"""
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute(create_users_table)
                await conn.commit()
                print("OK: Таблица users создана или уже существует")
        except Exception as e:
            print(f"ERROR: Ошибка создания таблицы: {e}")
            raise
    
    async def register_user(self, user_id: int, username: Optional[str], first_name: Optional[str]) -> bool:
        """
        Регистрирует нового пользователя в базе данных
        
        Args:
            user_id: ID пользователя Telegram
            username: Имя пользователя Telegram
            first_name: Имя пользователя Telegram
            
        Returns:
            True если пользователь успешно зарегистрирован, False если уже существует
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                # Проверяем, существует ли пользователь
                cursor = await conn.execute(
                    "SELECT id FROM users WHERE id = ?", (user_id,)
                )
                existing_user = await cursor.fetchone()
                
                if existing_user:
                    return False
                
                # Добавляем нового пользователя
                await conn.execute(
                    """
                    INSERT INTO users (id, username, first_name)
                    VALUES (?, ?, ?)
                    """,
                    (user_id, username, first_name)
                )
                await conn.commit()
                print(f"OK: Пользователь {user_id} зарегистрирован")
                return True
                
        except Exception as e:
            print(f"ERROR: Ошибка регистрации пользователя: {e}")
            raise
    
    async def get_user_info(self, user_id: int) -> Optional[dict]:
        """
        Получает информацию о пользователе
        
        Args:
            user_id: ID пользователя Telegram
            
        Returns:
            Словарь с информацией о пользователе или None если не найден
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute(
                    """
                    SELECT id, username, first_name, created_at
                    FROM users
                    WHERE id = ?
                    """,
                    (user_id,)
                )
                user_data = await cursor.fetchone()
                
                if user_data:
                    columns = ['id', 'username', 'first_name', 'created_at']
                    return dict(zip(columns, user_data))
                return None
                
        except Exception as e:
            print(f"ERROR: Ошибка получения информации о пользователе: {e}")
            raise


# Глобальный экземпляр базы данных
db = Database()
