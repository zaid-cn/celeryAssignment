from celery import shared_task
from celery.exceptions import Ignore
# from worker import app
# @app.task(bind=True)
@shared_task
def adding_task(x, y):
    return x + y
