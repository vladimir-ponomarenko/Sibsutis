# API Документация

Базовый URL: `http://localhost:8000/api`

Формат ответов: JSON  
Авторизация: JWT (Bearer)

## Аутентификация

### POST `/register/`
Регистрация пользователя.

Request JSON:
```json
{
  "username": "demo",
  "email": "demo@example.com",
  "password": "demo1234"
}
```

Response 201:
```json
{
  "id": 1,
  "username": "demo",
  "email": "demo@example.com"
}
```

Пример curl:
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@example.com","password":"demo1234"}'
```

### POST `/login/`
Получение JWT access token.

Request JSON:
```json
{
  "username": "demo",
  "password": "demo1234"
}
```

Response 200:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

Пример curl:
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}'
```

## Видео

### GET `/videos/`
Список видео (публично).

Response 200:
```json
[
  {
    "id": 1,
    "title": "Первое видео",
    "description": "Описание",
    "video_file": "http://localhost:8000/media/videos/demo.mp4",
    "uploaded_at": "2026-03-23T12:00:00Z",
    "uploaded_by": 1
  }
]
```

Пример curl:
```bash
curl http://localhost:8000/api/videos/
```

### POST `/upload/`
Загрузка видео (JWT required).

FormData:
- `title` (string)
- `description` (string)
- `video_file` (file)

Headers:
```
Authorization: Bearer <access_token>
```

Пример curl:
```bash
curl -X POST http://localhost:8000/api/upload/ \
  -H "Authorization: Bearer <access_token>" \
  -F "title=Демо" \
  -F "description=Описание" \
  -F "video_file=@/path/to/video.mp4"
```

Response 201:
```json
{
  "id": 1,
  "title": "Демо",
  "description": "Описание",
  "video_file": "http://localhost:8000/media/videos/demo.mp4",
  "uploaded_at": "2026-03-23T12:00:00Z",
  "uploaded_by": 1
}
```

### GET `/videos/{id}/`
Детали видео (публично).

Response 200:
```json
{
  "id": 1,
  "title": "Демо",
  "description": "Описание",
  "video_file": "http://localhost:8000/media/videos/demo.mp4",
  "uploaded_at": "2026-03-23T12:00:00Z",
  "uploaded_by": 1
}
```

Пример curl:
```bash
curl http://localhost:8000/api/videos/1/
```

### GET `/videos/{id}/thumbnail`
Превью (заглушка 1x1 PNG).

Response 200: `image/png`

Пример:
```bash
curl http://localhost:8000/api/videos/1/thumbnail --output thumb.png
```

## Коды ошибок
- `400` — неверные данные запроса
- `401` — нет или неверный JWT токен
- `404` — объект не найден
- `500` — ошибка сервера

## Быстрый сценарий работы
1. `POST /register/` — создать пользователя  
2. `POST /login/` — получить `access`  
3. `POST /upload/` — загрузить видео  
4. `GET /videos/` — получить список  
5. `GET /videos/{id}/` — открыть конкретное видео  
