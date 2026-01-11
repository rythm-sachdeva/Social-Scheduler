from celery import shared_task
from django.utils import timezone
from .models import SchedulePost, Status
from django.db import transaction
from .services import Poster 
from linkedinposter.services import LinkedInAdapter


@shared_task
def check_for_scheduled_posts():
    """
    Checks For the scheduled post using database polling
    """

    now = timezone.now()

    with transaction.atomic():
        post_due = SchedulePost.objects.select_for_update(skip_locked=True).filter(status=Status.SCHEDULED,scheduled_time__lte=now)

        for post in post_due:
            post.status = Status.PROCESSING
            post.save()

            publish_task.delay(post.id)


@shared_task(bind=True,max_retries=3)
def publish_task(self,post_id: str):
    """
    Celery Task to Publish the scheduled post
    """

    try:
        post = SchedulePost.objects.get(id=post_id)
        
        poster_service = Poster(adapter=LinkedInAdapter())
        poster_service.post_to_social_media(post)
        post.status = Status.PUBLISHED
        post.save()        
    except Exception as e:
        post.status = Status.FAILED
        post.error_message = str(e)
        post.error_log = str(e)
        post.save()
        raise self.retry(exc=e, countdown=60)
        