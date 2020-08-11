from celery.schedules import crontab
from datetime import timedelta
import datetime as dt
from celery import schedules


CELERY_IMPORTS = ('my_app.tasks.task')
BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_RESULT_BACKEND = 'db+sqlite:///my_app/my_app.db'
CELERY_RESULT_PERSISTENT = True
CELERY_TASK_RESULT_EXPIRES = 3600
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/London'

beat_dburi = 'sqlite:///my_app/my_app.db'
login_dburi = 'sqlite:///my_app.db'