"""
FastAPI сервер для Telegram Mini App календаря
"""
import os
import asyncio
from datetime import datetime, date
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import asyncpg

# Импорты для подключения к базе данных
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import Database

# Модели Pydantic
class EventCreate(BaseModel):
    user_id: int
    title: str
    event_date: date
    event_time: Optional[str] = None
    description: Optional[str] = None

class Event(BaseModel):
    id: int
    user_id: int
    title: str
    event_date: date
    event_time: Optional[str]
    description: Optional[str]
    created_at: datetime

# Создаем FastAPI приложение
app = FastAPI(title="JARVIS Calendar API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальная переменная для базы данных
db = None

@app.on_event("startup")
async def startup():
    """Инициализация базы данных при запуске"""
    global db
    db = Database()
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    """Закрытие соединения с базой данных при завершении"""
    global db
    if db and db.pool:
        await db.disconnect()

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "JARVIS Calendar API"}

@app.get("/api/events")
async def get_events(
    user_id: int = Query(...),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    """Получить события пользователя"""
    try:
        if year and month:
            events = await db.get_events_by_month(user_id, year, month)
        else:
            events = await db.get_events(user_id)
        
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events/day")
async def get_events_by_date(
    user_id: int = Query(...),
    date: date = Query(...)
):
    """Получить события на конкретную дату"""
    try:
        events = await db.get_events_by_date(user_id, date)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/events")
async def create_event(event: EventCreate):
    """Создать новое событие"""
    try:
        # Конвертируем время если нужно
        event_time = None
        if event.event_time:
            try:
                # Преобразуем строку времени в объект time
                time_parts = event.event_time.split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                event_time = datetime.time(hour, minute)
            except (ValueError, IndexError):
                pass
        
        success = await db.add_event(
            event.user_id,
            event.title,
            event.event_date,
            event_time,
            event.description
        )
        
        if success:
            return {"message": "Событие создано успешно"}
        else:
            raise HTTPException(status_code=500, detail="Ошибка создания события")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/events/{event_id}")
async def delete_event(event_id: int, user_id: int = Query(...)):
    """Удалить событие"""
    try:
        success = await db.delete_event(event_id, user_id)
        
        if success:
            return {"message": "Событие удалено успешно"}
        else:
            raise HTTPException(status_code=404, detail="Событие не найдено")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Обслуживание статических файлов
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
