# 🚀 Deployment Guide: ARMOR на Render

## 📋 Структура проекта

```
ARMOR/
├── app0/                    # Django проект
│   ├── app0/               # Main Django app
│   │   ├── settings.py     # Django настройки
│   │   ├── urls.py         # URL routes
│   │   ├── wsgi.py         # WSGI для веб-сервера
│   │   ├── asgi.py         # ASGI для WebSocket (Channels)
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── admin.py
│   │   ├── templates/      # HTML шаблоны
│   │   ├── static/         # CSS, JS, изображения
│   │   ├── media/          # Загруженные файлы
│   │   └── migrations/     # БД миграции
│   ├── chat/               # Django приложение чата
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── consumers.py    # WebSocket consumers (Channels)
│   │   ├── routing.py      # WebSocket маршруты
│   │   ├── urls.py
│   │   └── migrations/
│   ├── manage.py           # Django CLI
│   └── db.sqlite3          # БД (локально)
├── chat_server.py          # Отдельный WebSocket сервер (Background Worker)
├── Procfile                # Процессы для Render
├── build.sh                # Скрипт сборки
├── runtime.txt             # Python версия
├── requirements.txt        # Python зависимости
└── .env.example            # Пример переменных окружения
```

## 🔧 Что было исправлено

### 1. **Пути импортов (Django imports)**
❌ Было: `DJANGO_SETTINGS_MODULE=app0.app0.settings`  
✅ Стало: `DJANGO_SETTINGS_MODULE=app0.settings`

Файлы:
- [app0/manage.py](app0/manage.py#L8)
- [app0/app0/wsgi.py](app0/app0/wsgi.py#L4)
- [app0/app0/asgi.py](app0/app0/asgi.py#L7)
- [app0/app0/settings.py](app0/app0/settings.py#L51)

### 2. **Статические файлы и медиа**
✅ **settings.py** обновлен:
```python
# Статика работает по-разному на локалке и на Render
STATICFILES_DIRS = [BASE_DIR / 'app0' / 'static'] if DEBUG else []
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Медиа файлы поднялись на уровень выше для доступности
MEDIA_ROOT = BASE_DIR / 'media'
```

### 3. **Channels и WebSocket**
✅ **settings.py** содержит:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
```

### 4. **Procfile - два процесса**
```
web: cd app0 && python manage.py migrate && daphne -b 0.0.0.0 -p $PORT app0.asgi:application
chat: python chat_server.py
```

### 5. **Security настройки**
✅ SSL redirect, secure cookies и HSTS включены в production:
```python
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
```

## 📦 Требования установлены в requirements.txt
- `whitenoise>=6.6.0` - служит статичные файлы
- `daphne>=4.1.0` - ASGI сервер (для WebSocket)
- `channels>=4.0.0` - WebSocket поддержка Django
- `python-dotenv>=1.0.0` - загрузка переменных окружения

## 🌍 Развертывание на Render

### Шаг 1: Создать Web Service

1. Перейти на [render.com](https://render.com)
2. Создать новый **Web Service**
3. Подключить GitHub репозиторий

**Настройки Web Service:**
- **Build Command:** `bash build.sh`
- **Start Command:** `cd app0 && daphne -b 0.0.0.0 -p $PORT app0.asgi:application`
- **Environment:** Production

**Переменные окружения:**
```
DEBUG=False
SECRET_KEY=<GENERATE-RANDOM-STRING>
DJANGO_SETTINGS_MODULE=app0.settings
ALLOWED_HOSTS=yourdomain.onrender.com,yourotherdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### Шаг 2: Создать Background Worker (для chat_server.py)

1. Создать новый **Background Worker**
2. Подключить тот же репозиторий

**Настройки Background Worker:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python chat_server.py`

**Переменные окружения:**
```
CHAT_PORT=3001
DEBUG=False
```

### Шаг 3: Настроить PostgreSQL (опционально, вместо SQLite)

Если используете SQLite - пропустите.

Если нужна PostgreSQL:
1. Создать Render PostgreSQL
2. Скопировать `DATABASE_URL` из PostgreSQL сервиса
3. Добавить в Web Service переменную: `DATABASE_URL=<copied-url>`

### Шаг 4: Переменные окружения для Web Service

Скопируйте из файла [.env.example](.env.example) и отредактируйте:

| Переменная | Значение | Примечание |
|-----------|---------|-----------|
| `DEBUG` | `False` | Никогда True в production! |
| `SECRET_KEY` | Случайная строка 50+ символов | Сгенерировать: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DJANGO_SETTINGS_MODULE` | `app0.settings` | Не меняйте |
| `ALLOWED_HOSTS` | `yourdomain.onrender.com` | Добавьте домены |
| `SECURE_SSL_REDIRECT` | `True` | Редирект на HTTPS |
| `SESSION_COOKIE_SECURE` | `True` | Cookies только через HTTPS |
| `CSRF_COOKIE_SECURE` | `True` | CSRF защита через HTTPS |

## 📝 Команды для локальной разработки

### Первый запуск
```bash
cd app0
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### В отдельном терминале запустить чат-сервер
```bash
python chat_server.py
```

### Созданий суперпользователя
```bash
cd app0
python manage.py createsuperuser
```

### Запуск миграций
```bash
cd app0
python manage.py migrate
```

### Сборка статичных файлов
```bash
cd app0
python manage.py collectstatic --noinput
```

## 🐛 Решение ошибок

### Ошибка: `ModuleNotFoundError: No module named 'app0.settings'`
**Решение:** Проверьте `DJANGO_SETTINGS_MODULE` переменную (должна быть `app0.settings`, не `app0.app0.settings`)

### Ошибка: `no such table: app0_news`
**Решение:** Запустить миграции:
```bash
cd app0
python manage.py migrate
```

### Ошибка: `403 Forbidden` на статичных файлах
**Решение:** 
1. Убедитесь, что `whitenoise` в requirements.txt
2. Запустить: `python manage.py collectstatic --noinput`
3. Проверить `STATIC_ROOT` и `STATIC_URL` в settings.py

### Ошибка: WebSocket не подключается
**Решение:**
1. Убедитесь, что Background Worker запущен
2. Проверьте, что `ALLOWED_HOSTS` содержит ваш домен
3. Проверьте, что WebSocket URL правильный в фронтенде (должен быть `wss://` для HTTPS)

### Ошибка: Миграции не применяются на Render
**Решение:** Procfile автоматически запускает `python manage.py migrate` перед стартом. Если не помогает:
1. Перезагрузить Web Service
2. Проверить логи: `render.com -> Your Service -> Logs`

## 📚 Файлы для проверки

Убедитесь, что эти файлы содержат правильные пути:

✅ [app0/manage.py](app0/manage.py) - `DJANGO_SETTINGS_MODULE='app0.settings'`  
✅ [app0/app0/wsgi.py](app0/app0/wsgi.py) - `DJANGO_SETTINGS_MODULE='app0.settings'` + `whitenoise`  
✅ [app0/app0/asgi.py](app0/app0/asgi.py) - `DJANGO_SETTINGS_MODULE='app0.settings'` + imports из `chat.routing`  
✅ [app0/app0/settings.py](app0/app0/settings.py) - все пути и Security settings  
✅ [Procfile](Procfile) - правильные команды для двух процессов  
✅ [requirements.txt](requirements.txt) - все зависимости + whitenoise  
✅ [chat_server.py](../chat_server.py) - слушает на 0.0.0.0  

## 🔗 Полезные ссылки

- [Render Documentation](https://render.com/docs)
- [Django on Render](https://render.com/docs/deploy-django)
- [Channels Documentation](https://channels.readthedocs.io/)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)

---

**Готово! 🎉 Проект готов к развертыванию на Render**
