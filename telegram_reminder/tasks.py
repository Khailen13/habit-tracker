from celery import shared_task

from telegram_reminder.services import send_telegram_messages


@shared_task
def remind_about_habit():
    """Отправляет напоминание о привычке через Телеграм"""

    send_telegram_messages()
