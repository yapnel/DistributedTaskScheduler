start cmd /k ".\env\Scripts\Activate && celery -A my_app.worker.celery worker -l info --pool=solo -n wkr2"