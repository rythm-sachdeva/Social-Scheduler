from celery import shared_task
from django.utils import timezone
from poster.models import SchedulePost, Status
from django.db import transaction
from poster.services import Poster 
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
            pass


@shared_task(bind=True,max_retries=3)
def publish_task(self,post: SchedulePost):
    """
    Celery Task to Publish the scheduled post
    """

    try:
        poster_service = Poster(adapter=LinkedInAdapter(post))
        poster_service.post_to_social_media(post)
    except Exception as e:
        post.status = Status.FAILED
        post.error_message = str(e)
        post.error_log = str(e)
        post.save()
        raise self.retry(exc=e, countdown=60)
        