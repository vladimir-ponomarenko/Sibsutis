# Веб-Технологии РГР

Создание тестовой видеоплатформы с использованием технологий Python
для бэкенда, React JS для фронтенда и Figma для дизайна

## Возможности
- Регистрация и вход с JWT.
- Загрузка видео и обложек.
- Потоковое воспроизведение с поддержкой Range-запросов.
- Библиотека видео, страница трансляции, вспомогательные страницы из макетов.

## Структура
- `backend/` — Django проект.
- `videos/` — приложение с моделями и API.
- `frontend/` — React приложение.
- `docs/` — документация API.
- `report/` — отчёт.

## Быстрый старт (обновлено под `frontend/` + `backend/`)

### 1. Бэкенд (`backend/`)
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
python manage.py migrate
python manage.py runserver
```

> Если Postgres недоступен, используйте `USE_SQLITE=1` для локального запуска.

### 2. Фронтенд (`frontend/`)
```bash
cd frontend
npm install
npm start
```

Приложение будет доступно на `http://localhost:3000`.

## Тестирование
```bash
USE_SQLITE=1 python manage.py test
```

## Документация API
Смотрите `docs/api.md`.
