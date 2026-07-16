web: gunicorn alumed.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
bot: python manage.py telegram_bot
