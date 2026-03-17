# JARVIS Telegram Bot

🤖 Умный Telegram-бот на основе AI с использованием Groq API

## Стек технологий

- **aiogram 3.7** - фреймворк для создания Telegram ботов
- **asyncpg** - асинхронный драйвер PostgreSQL
- **python-dotenv** - управление переменными окружения
- **groq** - клиент для Groq API (модель Llama 3.3 70B)
- **APScheduler** - планировщик задач для напоминаний
- **google-api-python-client** - Google Calendar API
- **spotipy** - Spotify Web API

## Функционал

### 🤖 AI-чат
- 📝 Регистрация пользователей в базе данных
- 🤖 AI-чат с моделью Llama 3.3 70B через Groq
- 💾 История диалогов (последние 20 сообщений)
- 🗑️ Очистка истории командой `/clear`
- 🇷🇺 Ответы на русском языке с саркастичным стилем JARVIS

### 📝 Заметки
- `/note <текст>` - быстро создать заметку
- `/notes` - показать последние 10 заметок
- `/note_find <запрос>` - поиск по заметкам
- `/note_del <id>` - удалить заметку

### ⏰ Напоминания
- `/remind <время> <текст>` - создать напоминание
- `/reminders` - показать активные напоминания
- `/remind_del <id>` - удалить напоминание
- Форматы времени: `10min`, `2h`, `18:30`
- Автоматическая отправка в указанное время

### 📅 Google Calendar
- `/today` - события на сегодня
- `/week` - события на ближайшие 7 дней
- `/add_event <дата> <время> <название>` - создать событие
- Форматы: DD.MM или DD.MM.YYYY, время HH:MM

### 🎵 Spotify
- `/now` - что сейчас играет с прогресс-баром
- `/pause` - пауза/возобновление
- `/next` / `/prev` - переключение треков
- `/volume <0-100>` - громкость
- `/playlists` - показать плейлисты
- `/play <номер>` - включить плейлист

### 📋 Главное меню
ReplyKeyboard с кнопками:
- 💬 Чат, 📝 Заметки, 🔔 Напоминания
- 📅 Расписание, 🎵 Музыка, ⚙️ Настройки

## Установка и запуск

### 1. Клонирование и установка зависимостей

```bash
cd jarvis
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и заполните необходимые переменные:

```bash
cp .env.example .env
```

Обязательно заполните:
- `BOT_TOKEN` - токен вашего Telegram бота
- `GROQ_API_KEY` - API ключ от Groq
- `DATABASE_URL` - URL подключения к PostgreSQL

### Опционально (для расширенного функционала):
- `GOOGLE_CREDENTIALS` - base64 от credentials.json (Google Calendar)
- `SPOTIFY_CLIENT_ID` - Client ID Spotify приложения
- `SPOTIFY_CLIENT_SECRET` - Client Secret Spotify приложения
- `SPOTIFY_REDIRECT_URI` - Redirect URI для Spotify OAuth

### 3. Настройка базы данных

Убедитесь, что у вас есть база данных PostgreSQL. Бот автоматически создаст таблицы:
- `users` - информация о пользователях
- `notes` - заметки пользователей
- `reminders` - напоминания пользователей

### 4. Настройка интеграций (опционально)

#### Google Calendar
1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Calendar API
3. Создайте учетные данные OAuth 2.0
4. Скачайте credentials.json и закодируйте в base64
5. Добавьте в `.env` переменную `GOOGLE_CREDENTIALS`

#### Spotify
1. Создайте приложение в [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Получите Client ID и Client Secret
3. Добавьте Redirect URI: `http://127.0.0.1:8888/callback`
4. Добавьте переменные в `.env`

### 5. Запуск бота

```bash
python bot.py
```

## Развертывание на Railway

Проект готов к развертыванию на Railway. Просто загрузите код и установите переменные окружения в настройках проекта.

## Структура проекта

```
jarvis/
├── bot.py              # точка входа, запуск бота
├── config.py           # загрузка .env переменных
├── database.py         # подключение к PostgreSQL, работа с БД
├── handlers/
│   ├── __init__.py
│   ├── start.py        # /start — приветствие, регистрация
│   └── ai_chat.py      # обработка текстовых сообщений
├── services/
│   ├── __init__.py
│   └── groq_client.py  # клиент Groq API, история диалогов
├── .env.example        # пример переменных окружения
├── .env               # ваши переменные окружения
├── requirements.txt    # зависимости Python
├── Procfile           # для Railway
└── README.md          # этот файл
```

## Команды бота

- `/start` - приветствие и регистрация
- `/clear` - очистка истории диалога
- Любое текстовое сообщение - ответ от AI

## Особенности

- История диалогов хранится в памяти (по 20 сообщений на пользователя)
- Автоматическая регистрация новых пользователей
- Обработка ошибок с информативными сообщениями
- Логирование всех операций
- Готовность к развертыванию на Railway

## Лицензия

MIT License
