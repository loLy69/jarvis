"""
Модуль для работы с базой данных PostgreSQL через asyncpg
"""
import asyncpg
from typing import Optional
from config import Config


class Database:
    """Класс для управления подключением к базе данных"""
    
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Создает пул подключений к базе данных"""
        try:
            self.pool = await asyncpg.create_pool(
                Config.DATABASE_URL,
                min_size=1,
                max_size=10
            )
            print("OK: Подключение к базе данных установлено")
        except Exception as e:
            print(f"ERROR: Ошибка подключения к базе данных: {e}")
            raise
    
    async def disconnect(self):
        """Закрывает пул подключений"""
        if self.pool:
            await self.pool.close()
            print("CLOSE: Подключение к базе данных закрыто")
    
    async def create_tables(self):
        """Создает необходимые таблицы в базе данных"""
        if not self.pool:
            raise RuntimeError("Нет подключения к базе данных")
        
        # SQL запрос для создания таблицы users
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # SQL запрос для создания таблицы notes
        create_notes_table = """
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # SQL запрос для создания таблицы reminders
        create_reminders_table = """
        CREATE TABLE IF NOT EXISTS reminders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            text TEXT NOT NULL,
            remind_at TIMESTAMP NOT NULL,
            is_done BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(create_users_table)
                await conn.execute(create_notes_table)
                await conn.execute(create_reminders_table)
                # Создание таблицы событий
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        title TEXT NOT NULL,
                        event_date DATE NOT NULL,
                        event_time TIME,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                logger.info("OK: База данных готова")
        except Exception as e:
            print(f"ERROR: Ошибка создания таблиц: {e}")
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
        if not self.pool:
            raise RuntimeError("Нет подключения к базе данных")
        
        try:
            async with self.pool.acquire() as conn:
                # Проверяем, существует ли пользователь
                existing_user = await conn.fetchval(
                    "SELECT id FROM users WHERE id = $1", user_id
                )
                
                if existing_user:
                    return False
                
                # Добавляем нового пользователя
                await conn.execute(
                    """
                    INSERT INTO users (id, username, first_name)
                    VALUES ($1, $2, $3)
                    """,
                    user_id, username, first_name
                )
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
        if not self.pool:
            raise RuntimeError("Нет подключения к базе данных")
        
        try:
            async with self.pool.acquire() as conn:
                user_data = await conn.fetchrow(
                    """
                    SELECT id, username, first_name, created_at
                    FROM users
                    WHERE id = $1
                    """,
                    user_id
                )
                
                if user_data:
                    return dict(user_data)
                return None
                
        except Exception as e:
            print(f"ERROR: Ошибка получения информации о пользователе: {e}")
            raise
    
    # Методы для работы с заметками
    async def add_note(self, user_id: int, title: str, content: str, tags: str = None) -> int:
        """Добавляет новую заметку"""
        if not self.pool:
            raise RuntimeError("Нет подключения к базе данных")
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(
                    """
                    INSERT INTO notes (user_id, title, content, tags)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                    """,
                    user_id, title, content, tags
                )
                return result['id']
        except Exception as e:
            print(f"ERROR: Ошибка добавления заметки: {e}")
            raise
    
    async def get_user_notes(self, user_id: int, limit: int = 10) -> list:
        """Получает последние заметки пользователя"""
        if not self.pool:
            raise RuntimeError("Нет подключения к базе данных")
        
        try:
            async with self.pool.acquire() as conn:
                notes = await conn.fetch(
                    """
                    SELECT id, title, content, tags, created_at, updated_at
                    FROM notes
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                    """,
                    user_id, limit
                )
                return [dict(note) for note in notes]
        except Exception as e:
            print(f"ERROR: Ошибка получения заметок: {e}")
            raise
    
    async def search_notes(self, user_id: int, query: str) -> list:
        """Ищет заметки по заголовку и содержимому"""
        if not self.pool:
            raise RuntimeError("Нет подключения к базе данных")
        
        try:
            async with self.pool.acquire() as conn:
                notes = await conn.fetch(
                    """
                    SELECT id, title, content, tags, created_at, updated_at
                    FROM notes
                    WHERE user_id = $1 AND (title ILIKE $2 OR content ILIKE $2)
                    ORDER BY created_at DESC
                    """,
                    user_id, f"%{query}%"
                )
                return [dict(note) for note in notes]
        except Exception as e:
            print(f"ERROR: Ошибка поиска заметок: {e}")
            raise
    
    async def delete_note(self, user_id: int, note_id: int) -> bool:
        """Удаляет заметку"""
        if not self.pool:
            raise RuntimeError("Нет подключения к базе данных")
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(
                    """
                    DELETE FROM notes
                    WHERE id = $1 AND user_id = $2
                    """,
                    note_id, user_id
                )
                return result != "DELETE 0"
        except Exception as e:
            print(f"ERROR: Ошибка удаления заметки: {e}")
            raise
    
    # Методы для работы с напоминаниями
    async def add_reminder(self, user_id: int, text: str, remind_at) -> int:
        """Добавляет новое напоминание"""
        if not self.pool:
            raise RuntimeError("Нет подключения к базе данных")
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(
                    """
                    INSERT INTO reminders (user_id, text, remind_at)
                    VALUES ($1, $2, $3)
                    RETURNING id
                    """,
                    user_id, text, remind_at
                )
                return result['id']
        except Exception as e:
            print(f"ERROR: Ошибка добавления напоминания: {e}")
            raise
    
    async def get_user_reminders(self, user_id: int) -> list:
        """Получает активные напоминания пользователя"""
        if not self.pool:
            raise RuntimeError("Нет подключения к базе данных")
        
        try:
            async with self.pool.acquire() as conn:
                reminders = await conn.fetch(
                    """
                    SELECT id, text, remind_at, is_done, created_at
                    FROM reminders
                    WHERE user_id = $1 AND is_done = FALSE
                    ORDER BY remind_at ASC
                    """,
                    user_id
                )
                return [dict(reminder) for reminder in reminders]
        except Exception as e:
            print(f"ERROR: Ошибка получения напоминаний: {e}")
            raise
    
    async def delete_reminder(self, user_id: int, reminder_id: int) -> bool:
        """Удаляет напоминание"""
        if not self.pool:
            raise RuntimeError("Нет подключения к базе данных")
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(
                    """
                    DELETE FROM reminders
                    WHERE id = $1 AND user_id = $2
                    """,
                    reminder_id, user_id
                )
                return result != "DELETE 0"
        except Exception as e:
            print(f"ERROR: Ошибка удаления напоминания: {e}")
            raise
    
    async def get_pending_reminders(self) -> list:
        """Получает все неотправленные напоминания"""
        if not self.pool:
            raise RuntimeError("Нет подключения к базе данных")
        
        try:
            async with self.pool.acquire() as conn:
                reminders = await conn.fetch(
                    """
                    SELECT id, user_id, text, remind_at
                    FROM reminders
                    WHERE remind_at <= NOW() AND is_done = FALSE
                    ORDER BY remind_at ASC
                    """
                )
                return [dict(reminder) for reminder in reminders]
        except Exception as e:
            print(f"ERROR: Ошибка получения ожидающих напоминаний: {e}")
            raise
    
    async def mark_reminder_done(self, reminder_id: int) -> bool:
        """Отмечает напоминание как выполненное"""
        if not self.pool:
            raise RuntimeError("Нет подключения к базе данных")
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(
                    """
                    UPDATE reminders
                    SET is_done = TRUE
                    WHERE id = $1
                    """,
                    reminder_id
                )
                return result != "UPDATE 0"
        except Exception as e:
            print(f"ERROR: Ошибка отметки напоминания: {e}")
            raise

    async def get_events(self, user_id: int, start_date: Optional[datetime.date] = None, 
                        end_date: Optional[datetime.date] = None) -> List[Dict]:
        """
        Получить события пользователя за период
        
        Args:
            user_id: ID пользователя
            start_date: Начальная дата (опционально)
            end_date: Конечная дата (опционально)
            
        Returns:
            Список событий
        """
        try:
            async with self.pool.acquire() as conn:
                if start_date and end_date:
                    query = """
                        SELECT id, title, event_date, event_time, description, created_at
                        FROM events 
                        WHERE user_id = $1 AND event_date BETWEEN $2 AND $3
                        ORDER BY event_date, event_time
                    """
                    rows = await conn.fetch(query, user_id, start_date, end_date)
                elif start_date:
                    query = """
                        SELECT id, title, event_date, event_time, description, created_at
                        FROM events 
                        WHERE user_id = $1 AND event_date >= $2
                        ORDER BY event_date, event_time
                    """
                    rows = await conn.fetch(query, user_id, start_date)
                else:
                    query = """
                        SELECT id, title, event_date, event_time, description, created_at
                        FROM events 
                        WHERE user_id = $1
                        ORDER BY event_date, event_time
                    """
                    rows = await conn.fetch(query, user_id)
                
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"ERROR: Ошибка получения событий: {e}")
            return []
    
    async def add_event(self, user_id: int, title: str, event_date: datetime.date, 
                       event_time: Optional[datetime.time] = None, 
                       description: Optional[str] = None) -> bool:
        """
        Добавить новое событие
        
        Args:
            user_id: ID пользователя
            title: Название события
            event_date: Дата события
            event_time: Время события (опционально)
            description: Описание (опционально)
            
        Returns:
            True если успешно
        """
        try:
            async with self.pool.acquire() as conn:
                query = """
                    INSERT INTO events (user_id, title, event_date, event_time, description)
                    VALUES ($1, $2, $3, $4, $5)
                """
                await conn.execute(query, user_id, title, event_date, event_time, description)
                return True
        except Exception as e:
            print(f"ERROR: Ошибка добавления события: {e}")
            return False
    
    async def delete_event(self, event_id: int, user_id: int) -> bool:
        """
        Удалить событие
        
        Args:
            event_id: ID события
            user_id: ID пользователя (для проверки)
            
        Returns:
            True если успешно
        """
        try:
            async with self.pool.acquire() as conn:
                query = "DELETE FROM events WHERE id = $1 AND user_id = $2"
                result = await conn.execute(query, event_id, user_id)
                return result == "DELETE 1"
        except Exception as e:
            print(f"ERROR: Ошибка удаления события: {e}")
            return False
    
    async def get_events_by_month(self, user_id: int, year: int, month: int) -> List[Dict]:
        """
        Получить события за месяц
        
        Args:
            user_id: ID пользователя
            year: Год
            month: Месяц (1-12)
            
        Returns:
            Список событий
        """
        try:
            start_date = datetime.date(year, month, 1)
            if month == 12:
                end_date = datetime.date(year + 1, 1, 1)
            else:
                end_date = datetime.date(year, month + 1, 1)
            
            return await self.get_events(user_id, start_date, end_date)
        except Exception as e:
            print(f"ERROR: Ошибка получения событий за месяц: {e}")
            return []
    
    async def get_events_by_date(self, user_id: int, date: datetime.date) -> List[Dict]:
        """
        Получить события на конкретную дату
        
        Args:
            user_id: ID пользователя
            date: Дата
            
        Returns:
            Список событий
        """
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT id, title, event_date, event_time, description, created_at
                    FROM events 
                    WHERE user_id = $1 AND event_date = $2
                    ORDER BY event_time
                """
                rows = await conn.fetch(query, user_id, date)
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"ERROR: Ошибка получения событий за дату: {e}")
            return []


# Глобальный экземпляр базы данных
db = Database()
