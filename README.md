# AI-HR Бот Эмили

Виртуальный HR-бот для проведения автоматизированных собеседований с использованием искусственного интеллекта.

## Основные функции

- Проведение интервью с динамической генерацией вопросов
- Анализ hard и soft skills кандидатов
- Голосовое взаимодействие через ElevenLabs
- Видеозвонки через LiveKit
- Автоматическое формирование отчетов в Google Sheets

## Установка

1. Клонируйте репозиторий
```bash
git clone https://github.com/your-repo/ai-hr-bot.git
cd ai-hr-bot
```

2. Установите зависимости
```bash
pip install -r requirements.txt
```

3. Создайте файл .env и добавьте необходимые переменные окружения:
```
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
GOOGLE_SHEETS_CREDENTIALS=path_to_credentials.json
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret
```

4. Запустите сервер
```bash
uvicorn main:app --reload
```

## Структура проекта

- `main.py` - основной файл приложения
- `interview/` - модуль для проведения интервью
- `services/` - сервисы для работы с API
- `models/` - модели данных
- `config/` - конфигурационные файлы

## Технологии

- FastAPI
- LiveKit
- ElevenLabs
- OpenAI GPT-4
- Google Sheets API 