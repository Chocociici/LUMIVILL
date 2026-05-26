# 🎭 ARMOR - Django + WebSocket Chat

Полнофункциональный Django проект с отдельным WebSocket чат-сервером, готовый к развертыванию на Render.

## 🚀 Быстрый старт

### Локальная разработка

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd ARMOR

# 2. Создать виртуальное окружение
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Перейти в app0 и выполнить миграции
cd app0
python manage.py migrate

# 5. Создать суперпользователя
python manage.py createsuperuser

# 6. Запустить Django (Терминал 1)
python manage.py runserver

# 7. В другом терминале запустить чат-сервер (Терминал 2)
cd ..
python chat_server.py
```

Откройте http://localhost:8000 в браузере

### Production на Render

1. **Подготовка:**
   - Убедитесь что все переменные окружения установлены (см. [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md))
   - Проверьте [RENDER_DEPLOY.md](RENDER_DEPLOY.md) для полных инструкций

2. **Создание Web Service:**
   - Build Command: `bash build.sh`
   - Start Command: `cd app0 && daphne -b 0.0.0.0 -p $PORT app0.asgi:application`

3. **Создание Background Worker:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python chat_server.py`

4. **Переменные окружения:**
```
DEBUG=False
SECRET_KEY=<strong-random-key>
DJANGO_SETTINGS_MODULE=app0.settings
ALLOWED_HOSTS=yourapp.onrender.com
```

## 📁 Структура проекта

```
ARMOR/
├── app0/                      # Django проект
│   ├── app0/                  # Main app с настройками
│   │   ├── settings.py        # Django настройки ✅
│   │   ├── urls.py            # URL routes
│   │   ├── wsgi.py            # WSGI сервер ✅
│   │   ├── asgi.py            # ASGI для WebSocket ✅
│   │   ├── templates/         # HTML
│   │   ├── static/            # CSS, JS, images
│   │   └── media/             # User uploads
│   ├── chat/                  # Chat Django app
│   │   ├── consumers.py       # WebSocket handlers
│   │   ├── routing.py         # WebSocket routes
│   │   └── models.py
│   ├── manage.py              # Django CLI ✅
│   └── db.sqlite3             # Database
├── chat_server.py             # Отдельный WebSocket сервер ✅
├── Procfile                   # Render процессы ✅
├── build.sh                   # Build скрипт ✅
├── runtime.txt                # Python версия ✅
├── requirements.txt           # Зависимости ✅
├── render.yaml                # Render конфиг ✅
├── RENDER_DEPLOY.md           # Инструкции deployment
├── ENVIRONMENT_VARIABLES.md   # Документация переменных
└── .env.example               # Пример .env

```

## ✅ Что было исправлено

| Проблема | Решение | Файл |
|----------|---------|------|
| ❌ `ModuleNotFoundError: No module named 'app0.settings'` | ✅ Изменено на `app0.settings` (было `app0.app0.settings`) | manage.py, wsgi.py, asgi.py |
| ❌ `no such table: app0_news` | ✅ Автоматические миграции в Procfile | Procfile |
| ❌ Static files 404 | ✅ Добавлен WhiteNoise, исправлены пути | settings.py, requirements.txt |
| ❌ WebSocket не работает | ✅ Правильная конфигурация ASGI | asgi.py, settings.py |
| ❌ Пути импортов неправильные | ✅ Исправлены в `chat_server.py` и `asgi.py` | asgi.py, settings.py |
| ❌ Security issues | ✅ SSL redirect, secure cookies | settings.py |

## 🔧 Технологический стек

- **Django 4.2.11** - Web фреймворк
- **Channels 4.0.0** - WebSocket поддержка
- **Daphne 4.1.0** - ASGI сервер
- **websockets 12.0** - WebSocket библиотека для чат-сервера
- **WhiteNoise 6.6.0** - Статические файлы
- **Pillow 10.3.0** - Обработка изображений
- **PostgreSQL** - Production БД (опционально)

## 🐛 Решение распространённых ошибок

### Ошибка при импорте settings
```
ModuleNotFoundError: No module named 'app0.app0.settings'
```
**Решение:** Обновите переменную окружения:
```bash
DJANGO_SETTINGS_MODULE=app0.settings
```

### Статические файлы не загружаются (404)
```bash
# Собрать статические файлы
cd app0
python manage.py collectstatic --noinput
```

### WebSocket не подключается на production
1. Проверьте, что Background Worker запущен
2. Используйте `wss://` вместо `ws://` для HTTPS
3. Проверьте `ALLOWED_HOSTS`

### БД ошибки после deployment
```bash
# Вручную запустить миграции на Render
# (обычно это происходит автоматически в build.sh)
```

## 📚 Документация

- [RENDER_DEPLOY.md](RENDER_DEPLOY.md) - Полная инструкция для Render
- [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) - Документация переменных окружения
- [Официальная документация Django](https://docs.djangoproject.com/)
- [Channels Documentation](https://channels.readthedocs.io/)

## 🔐 Security Checklist

- ✅ `DEBUG=False` на production
- ✅ Уникальный `SECRET_KEY`
- ✅ SSL redirect включен
- ✅ Secure cookies
- ✅ CSRF protection
- ✅ ALLOWED_HOSTS правильно настроен
- ✅ Нет чувствительной информации в коде

## 💡 Tips

### Для локальной разработки
```bash
# Установить requirements
pip install -r requirements.txt

# Создать миграцию после изменений в models.py
python manage.py makemigrations

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Запустить тесты
python manage.py test
```

### Для production
```bash
# Собрать статические файлы
python manage.py collectstatic --noinput

# Запустить миграции
python manage.py migrate

# Проверить deployment готовность
python manage.py check --deploy
```

## 📞 Support

- GitHub Issues: [Link to Issues]
- Email: [Your Email]

## 📄 License

MIT License - see LICENSE file for details

---

**Проект готов к deployment! 🚀**
