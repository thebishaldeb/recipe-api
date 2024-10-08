import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from users.models import CustomUser
from recipe.models import RecipeLike
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Function to send notification email using celery queue 
@shared_task
def send_notification_email(subject, message, recipient_list):
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
        logger.info(f'Email sent to {recipient_list}')
    except Exception as e:
        logger.error(f'Error sending email: {e}')

# Function to check the number of likes using celery worker and beat 
@shared_task
def send_daily_notifications():
    logger.info('Task started: send_daily_notifications')
    try:
        yesterday = datetime.now() - timedelta(days=1)
        authors = CustomUser.objects.all()
        for author in authors:
            total_likes = RecipeLike.objects.filter(user=author, created__gte=yesterday).count()
            if total_likes > 0:
                subject = 'Daily Likes Notification'
                message = f'You received {total_likes} new likes on your recipes in the last 24 hours.'
                recipient_list = [author.email]
                send_notification_email.delay(subject, message, recipient_list)
    except Exception as e:
        logger.error(f'Error occurred: {e}')
    finally:
        logger.info('Task completed')
