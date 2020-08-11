start cmd /k ".\env\Scripts\Activate && waitress-serve --port=5000 my_app:app"
start cmd /k ".\env\Scripts\Activate && celery -A my_app.worker.celery worker -l info --pool=solo -n wkr1"
start cmd /k ".\env\Scripts\Activate && celery -A my_app.worker.celery beat -l info -S celery_sqlalchemy_scheduler.schedulers:DatabaseScheduler"
SLEEP 5
start cmd /k ".\env\Scripts\Activate && celery flower -A my_app.worker.celery -l info --broker_api=http://guest:guest@localhost:15672/api/ --persistent=True"


