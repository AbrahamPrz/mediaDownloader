from celery import shared_task
from celery_progress.backend import ProgressRecorder

from time import sleep

@shared_task(bind=True)
def go_to_sleep(self, progress, total):
    progress_recorder = ProgressRecorder(self)
    progress_recorder.set_progress(progress, total, 'On iteration')
    return 'Done'