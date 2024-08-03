web: gunicorn tagandtake.wsgi --log-file -
worker: celery -A my_celery worker --loglevel=info
beat: celery -A my_celery beat --loglevel=info