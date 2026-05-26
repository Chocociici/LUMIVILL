# 🌍 Переменные окружения для ARMOR проекта

## 📋 Описание всех переменных

### Django Основные настройки

#### `DEBUG` (boolean)
- **Значение локально:** `True`
- **Значение на Render:** `False`
- **Описание:** Включает/отключает режим отладки Django
- ⚠️ **НИКОГДА не ставьте `True` на production!**

#### `SECRET_KEY` (string)
- **Значение:** Случайная строка 50+ символов
- **Описание:** Секретный ключ для безопасности Django
- **Как сгенерировать:**
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```
- ⚠️ **Никогда не коммитьте реальный SECRET_KEY в GitHub!**

#### `DJANGO_SETTINGS_MODULE` (string)
- **Значение:** `app0.settings`
- **Описание:** Путь к модулю настроек Django
- ⚠️ **Не меняйте это значение!**

---

### Хост и домены

#### `ALLOWED_HOSTS` (comma-separated string)
- **Значение локально:** `localhost,127.0.0.1`
- **Значение на Render:** `yourapp.onrender.com,yourdomain.com`
- **Описание:** Какие хосты могут обращаться к приложению
- **Пример:**
```
ALLOWED_HOSTS=armor.onrender.com,armor.example.com,localhost
```

#### `PORT` (integer)
- **Значение:** Автоматически устанавливается Render (обычно 10000)
- **Описание:** Порт для веб-сервера
- **Примечание:** На локальной машине игнорируется (Django runserver использует 8000)

---

### Security (Безопасность)

#### `SECURE_SSL_REDIRECT` (boolean)
- **Значение локально:** `False`
- **Значение на Render:** `True`
- **Описание:** Редирект всех HTTP запросов на HTTPS
- **Установка:** `SECURE_SSL_REDIRECT=True`

#### `SESSION_COOKIE_SECURE` (boolean)
- **Значение локально:** `False`
- **Значение на Render:** `True`
- **Описание:** Cookies отправляются только через HTTPS
- **Установка:** `SESSION_COOKIE_SECURE=True`

#### `CSRF_COOKIE_SECURE` (boolean)
- **Значение локально:** `False`
- **Значение на Render:** `True`
- **Описание:** CSRF токены отправляются только через HTTPS
- **Установка:** `CSRF_COOKIE_SECURE=True`

#### `SECURE_HSTS_SECONDS` (integer)
- **Значение локально:** `0`
- **Значение на Render:** `31536000` (1 год)
- **Описание:** HTTP Strict-Transport-Security header время жизни
- **Примечание:** Указывает браузерам использовать только HTTPS

---

### Чат-сервер WebSocket

#### `CHAT_PORT` (integer)
- **Значение локально:** `3001`
- **Значение на Render:** `3001`
- **Описание:** Порт для отдельного WebSocket чат-сервера
- **Примечание:** Используется только Background Worker

---

### Email (опционально)

#### `EMAIL_BACKEND` (string)
- **Значение локально:** `django.core.mail.backends.console.EmailBackend`
- **Значение на Render:** `django.core.mail.backends.smtp.EmailBackend`
- **Описание:** Бэкенд отправки писем
- **Опции:**
  - `console` - вывод в консоль (локально)
  - `filebased` - сохранение в файл
  - `smtp` - отправка через SMTP

#### `EMAIL_HOST` (string, опционально)
- **Пример:** `smtp.gmail.com`

#### `EMAIL_PORT` (integer, опционально)
- **Пример:** `587`

#### `EMAIL_HOST_USER` (string, опционально)
- **Пример:** `your-email@gmail.com`

#### `EMAIL_HOST_PASSWORD` (string, опционально)
- ⚠️ **Используйте App Password для Gmail, не основной пароль!**

---

### Логирование и Отладка

#### `PYTHONUNBUFFERED` (boolean)
- **Значение:** `true` (строка, не boolean)
- **Описание:** Выводит логи Django без буферизации (важно на Render)
- **Установка:** `PYTHONUNBUFFERED=true`

---

## 💾 Локальная разработка: .env файл

Создайте файл `.env` в корне проекта (не коммитьте в GitHub):

```bash
# app0/.env или просто .env в корне

# Django
DEBUG=True
SECRET_KEY=your-local-secret-key-can-be-simple-for-development
DJANGO_SETTINGS_MODULE=app0.settings

# Хосты
ALLOWED_HOSTS=localhost,127.0.0.1

# Security (отключено локально для удобства)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# WebSocket чат-сервер
CHAT_PORT=3001

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Затем загрузите их в Django:

```python
# app0/app0/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

---

## 🚀 Render: Установка переменных

### Через Render Dashboard

1. Перейти в Web Service
2. **Settings** → **Environment**
3. Добавить переменные:

```
DEBUG=False
SECRET_KEY=<generate-strong-key>
DJANGO_SETTINGS_MODULE=app0.settings
ALLOWED_HOSTS=armor.onrender.com,yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
PYTHONUNBUFFERED=true
```

### Через render.yaml

Переменные уже настроены в [render.yaml](render.yaml)

---

## 📝 Чек-лист перед deployment на Render

- [ ] Сгенерировано правильное значение `SECRET_KEY` (50+ символов)
- [ ] `DEBUG=False` установлено
- [ ] `ALLOWED_HOSTS` содержит ваш Render домен
- [ ] `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`
- [ ] Все переменные добавлены в Render Dashboard
- [ ] Миграции БД выполнены (`python manage.py migrate`)
- [ ] Статические файлы собраны (`python manage.py collectstatic`)
- [ ] Суперпользователь создан (`python manage.py createsuperuser`)
- [ ] requirements.txt содержит все зависимости
- [ ] Procfile содержит правильные команды

---

## 🔐 Безопасность

⚠️ **Критические точки:**

1. **Никогда** не коммитьте реальный `.env` файл в GitHub
2. **Никогда** не ставьте `DEBUG=True` на production
3. **Всегда** используйте HTTPS на production (`SECURE_SSL_REDIRECT=True`)
4. **Регулярно** ротируйте `SECRET_KEY`
5. **Используйте** сильные пароли для суперпользователя

---

## 📚 Дополнительно

- [Django Environment Variables](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Render Documentation](https://render.com/docs)
- [12Factor App Config](https://12factor.net/config)
