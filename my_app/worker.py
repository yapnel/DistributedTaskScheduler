from celery import Celery
import my_app.celeryconfig
from my_app.celeryconfig import beat_dburi

celery = Celery('worker')
celery.config_from_object('my_app.celeryconfig')

celery.conf.update(
    {'beat_dburi': beat_dburi}
)

