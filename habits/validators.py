from datetime import timedelta

from rest_framework import serializers

from habits.models import Habit


class DurationValidator:
    """Проверяет длительность действия привычки на непревышение 2 минут."""

    def __call__(self, attrs):
        duration = attrs.get("duration")
        duration_limit = timedelta(seconds=120)
        if duration > duration_limit:
            raise serializers.ValidationError("Время выполнения должно быть не больше 120 секунд.")


class PeriodicityValidator:
    """Проверяет условия для периодичности привычки:
    - если привычка - приятная: равно None;
    - если привычка - полезная: не превышает 7 и не равно 0 (в днях)."""

    def __call__(self, attrs):
        is_pleasant = attrs.get("is_pleasant")
        periodicity = attrs.get("periodicity")
        if is_pleasant:
            if periodicity:
                raise serializers.ValidationError("Для приятной привычки периодичность не указывается (None or null).")
        else:
            if not periodicity:
                raise serializers.ValidationError("Для полезной привычки необходимо указать периодичность.")
            elif periodicity == 0 or periodicity > 7:
                raise serializers.ValidationError("Периодичность привычки должна быть от 1 до 7 дней.")


class PleasantOrUsefulHabitValidator:
    """Проверяет следующие условия для привычки по атрибутам полезный и приятный:
    - у приятной привычки не может быть вознаграждения или связанной привычки;
    - у полезной привычки должно быть либо вознаграждение, либо связанная причина."""

    def __call__(self, attrs):
        is_pleasant = attrs.get("is_pleasant")
        award = attrs.get("award")
        related_habit = attrs.get("related_habit")
        if is_pleasant and (award or related_habit):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )
        if not is_pleasant and ((not award and not related_habit) or (award and related_habit)):
            raise serializers.ValidationError(
                "у полезной привычки должно быть либо вознаграждение, либо связанная причина."
            )


class RelatedHabitValidator:
    """Проверяет:
    - отсутствие ссылки объекта на самого себя по полю связанного ключа;
    - наличие у связанной привычки признака приятной привычки;
    - отсутствие связей у приятной привычки с полезными привычками при переключении атрибута приятности на False."""

    def __init__(self, habit):
        self.habit = habit

    def __call__(self, attrs):
        related_habit = attrs.get("related_habit")
        current_habit_is_pleasant = attrs.get("is_pleasant")
        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError("В поле связанная привычка можно указывать только приятную привычку.")
        if related_habit == self.habit:
            raise serializers.ValidationError("В поле связанная привычка нельзя указывать ту же самую привычку.")
        if not current_habit_is_pleasant:
            related_useful_habits = Habit.objects.filter(related_habit=self.habit)
            if related_useful_habits:
                related_useful_habits_pks = [habit.pk for habit in related_useful_habits]
                raise serializers.ValidationError(
                    f"На данную привычку, как на приятную, ссылаются полезные привычки id={related_useful_habits_pks}."
                    f"Перед изменением признака 'приятный' необходимо исправить эти ссылки."
                )
