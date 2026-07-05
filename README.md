# Booking Service

Сервис бронирования переговорных комнат в ковокринге.

## Технологический стек

- Python 3.11
- FastAPI
- PostgreSQL + SQLAlchemy
- Poetry
- Docker + Docker Compose
- Pytest

---

## Запуск приложения

Перед запуском скопируйте шаблон настроек в файл `.env`:
```bash
cp .env.example .env
```

### Запуск через Docker Compose
Сборка и запуск проекта одной командой:
```bash
docker-compose up --build
```
После этого API будет доступно по адресу: http://localhost:8000
Интерактивная документация (Swagger): http://localhost:8000/docs

---

## Примеры запросов к API

### 1. Регистрация нового пользователя
```bash
curl -X 'POST' \
  'http://localhost:8000/api/auth/register' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "ivan_dev",
  "email": "ivan@example.com",
  "password": "secretpassword123",
  "full_name": "Иван Иванов"
}'
```

### 2. Авторизация и получение токена
```bash
curl -X 'POST' \
  'http://localhost:8000/api/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=ivan_dev&password=secretpassword123'
```

### 3. Просмотр списка всех комнат
```bash
curl -X 'GET' \
  'http://localhost:8000/api/rooms'
```

### 4. Создание бронирования комнаты
```bash
curl -X 'POST' \
  'http://localhost:8000/api/bookings' \
  -H 'Authorization: Bearer <ваш_токен>' \
  -H 'Content-Type: application/json' \
  -d '{
  "room_id": 1,
  "slot_id": 1,
  "booking_date": "2026-07-05",
  "notes": "Встреча команды"
}'
```

---

## Запуск тестов

Для локального запуска автоматических тестов выполните:
```bash
poetry install
poetry run pytest -v
```

---

## Автор проекта

- **ФИО:** Неупокоев Никита
- **Email:** [n.neupokoev154@yandex.ru](mailto:n.neupokoev154@yandex.ru)
- **Telegram:** [@NikitaNeupokoev](https://t.me)
