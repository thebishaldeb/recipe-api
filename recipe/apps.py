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
        timezone='Asia/Kolkata'
    )

    task_name = 'Send daily notifications'
    task, created = PeriodicTask.objects.get_or_create(
        name=task_name,
        defaults={
            'crontab': schedule,
            'task': 'recipe.tasks.send_daily_notifications',
        }
    )

    if not created:
        task.crontab = schedule
        task.task = 'recipe.tasks.send_daily_notifications'
        task.save()


class RecipeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipe'

    def ready(self):
        post_migrate.connect(setup_periodic_tasks, sender=self)
