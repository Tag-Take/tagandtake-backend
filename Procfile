web: gunicorn config.wsgi --log-file -
worker: celery -A async_tasks worker --loglevel=info
beat: celery -A async_tasks beat --loglevel=info