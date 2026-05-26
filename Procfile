web: cd app0 && python manage.py migrate --noinput && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p $PORT app0.asgi:application
chat: python chat_server.py