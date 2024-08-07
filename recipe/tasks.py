from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from users.models import CustomUser
from recipe.models import Recipe, RecipeLike
from datetime import datetime, timedelta

@shared_task
def send_notification_email(subject, message, recipient_list):
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

@shared_task
def send_daily_notifications():
    yesterday = datetime.now() - timedelta(days=1)
    authors = CustomUser.objects.all()
    
    for author in authors:
        total_likes = RecipeLike.objects.filter(user=author, created__gte=yesterday).count()

        if total_likes > 0:
            subject = 'Daily Likes Notification'
            message = f'You received {total_likes} new likes on your recipes in the last 24 hours.'
            recipient_list = [author.email]
            send_notification_email.delay(subject, message, recipient_list)
