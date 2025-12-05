import pytz  # Импортируем библиотеку для работы с часовыми поясами
import requests
from django.utils import timezone

from config import settings
from habits.models import Habit


def send_telegram_messages():

    now_utc = timezone.now()
    local_tz = pytz.timezone(settings.TIME_ZONE)
    local_now = now_utc.astimezone(local_tz)
    next_time = local_now + timezone.timedelta(minutes=15)
    all_habits = Habit.objects.all()
    selected_habits = [habit for habit in all_habits if (local_now <= habit.next_execution_datetime < next_time)]
    if selected_habits:
        for habit in selected_habits:
            action = habit.action
            time = habit.time
            place = habit.place
            duration = int(habit.duration.total_seconds())
            sweet = habit.award if habit.award else habit.related_habit
            message = (
                f"Привет! 👋 \nНапоминаю об атомной привычке💫\n"
                f"Действие: {action}.\nМесто: {place}.\nВремя: {time}.\n"
                f"Займет {duration} сек.\nА потом {sweet}! 👑🌟🎉"
            )
            habit.last_execution_datetime = habit.next_execution_datetime
            habit.next_execution_datetime += timezone.timedelta(days=habit.periodicity)
            habit.save()
            params = {"chat_id": habit.user.tg_chat_id, "text": message}
            requests.get(f"{settings.TELEGRAM_URL}{settings.TELEGRAM_TOKEN}/sendMessage", params=params)
