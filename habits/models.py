from django.db import models

from users.models import User


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    place = models.CharField(max_length=250, verbose_name="Место")
    time = models.TimeField(null=True, verbose_name="Время в формате HH:MM[:ss]")
    action = models.CharField(max_length=500, verbose_name="Действие")
    is_pleasant = models.BooleanField(verbose_name="Признак приятной привычки")
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
    )
    award = models.CharField(max_length=500, null=True, blank=True, verbose_name="Вознаграждение")
    duration = models.DurationField(verbose_name="Время на выполнение")
    periodicity = models.PositiveSmallIntegerField(default=1, null=True, blank=True, verbose_name="Периодичность")
    public_flag = models.BooleanField(default=False, verbose_name="Признак публичности")
    last_execution_datetime = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        verbose_name="Дата и время последнего выполнения",
    )
    next_execution_datetime = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата и время следующего выполнения",
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def __str__(self):
        return str(self.pk)
