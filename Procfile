web: gunicorn -w 5 spendb.core:create_web_app --log-file -
worker: celery -A spendb.tasks worker -c 2 -l debug
