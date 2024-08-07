from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django_celery_beat.models import PeriodicTask, IntervalSchedule

def setup_periodic_tasks(sender, **kwargs):
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.DAYS,
    )

    PeriodicTask.objects.get_or_create(
        interval=schedule,
        name='Send daily notifications',
        task='recipe.tasks.send_daily_notifications',
    )

class RecipeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipe'

    def ready(self):
        post_migrate.connect(setup_periodic_tasks, sender=self)
