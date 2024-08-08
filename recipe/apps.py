from django.apps import AppConfig
from django.db.models.signals import post_migrate

def setup_periodic_tasks(sender, **kwargs):
    from django_celery_beat.models import PeriodicTask, CrontabSchedule
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour='8',
        day_of_week='*',  
        day_of_month='*',  
        month_of_year='*',  
    )

    PeriodicTask.objects.get_or_create(
        crontab=schedule,
        name='Send daily notifications',
        task='recipe.tasks.send_daily_notifications',
    )

class RecipeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipe'

    def ready(self):
        post_migrate.connect(setup_periodic_tasks, sender=self)
