web: gunicorn -w 5 spendb.wsgi:app --log-file -
worker: celery -A spendb.tasks worker -c 2 -l debug
