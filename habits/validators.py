from datetime import timedelta

from rest_framework import serializers

from habits.models import Habit


class HabitValidator:
    """Родительский класс для валидаторов.
    При создании объекта, а также при обновлении с заполнением поля использует вводимые значения,
    при обновлении без заполнения поля использует существующие значения."""

    def __init__(self, user, habit, method):
        self.habit = habit
        self.method = method
        self.user = user

    def get_attribute(self, attrs, key):
        # Проверяем условия для POST и (PATCH/PUT с ключом в attrs)
        if self.method == "POST" or (self.method in ["PATCH", "PUT"] and key in attrs):
            return attrs.get(key)
        # В остальных случаях берем значение из существующей модели
        return getattr(self.habit, key)


class DurationValidator(HabitValidator):
    """Проверяет длительность действия привычки на непревышение 2 минут."""

    def __call__(self, attrs):
        duration = self.get_attribute(attrs, "duration")
        if duration and duration > timedelta(seconds=120):
            raise serializers.ValidationError("Время выполнения должно быть не больше 120 секунд.")


class PeriodicityValidator(HabitValidator):
    """Проверяет условия для периодичности привычки:
    - если привычка - приятная: равно None;
    - если привычка - полезная: не превышает 7 и не равно 0 (в днях)."""

    def __call__(self, attrs):
        is_pleasant = self.get_attribute(attrs, "is_pleasant")
        periodicity = self.get_attribute(attrs, "periodicity")

        if is_pleasant:  # Проверяем, что значение существует
            if periodicity:
                raise serializers.ValidationError("Для приятной привычки периодичность не указывается (None or null).")
        else:
            if not periodicity:
                raise serializers.ValidationError("Для полезной привычки необходимо указать периодичность.")
            if periodicity == 0 or periodicity > 7:
                raise serializers.ValidationError("Периодичность привычки должна быть от 1 до 7 дней.")


class PleasantOrUsefulHabitValidator(HabitValidator):
    """Проверяет следующие условия для привычки по атрибутам полезный и приятный:
    - у приятной привычки не может быть вознаграждения или связанной привычки;
    - у полезной привычки должно быть либо вознаграждение, либо связанная причина."""

    def __call__(self, attrs):
        is_pleasant = self.get_attribute(attrs, "is_pleasant")
        award = self.get_attribute(attrs, "award")
        related_habit = self.get_attribute(attrs, "related_habit")

        if is_pleasant and (award or related_habit):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )
        if not is_pleasant and ((not award and not related_habit) or (award and related_habit)):
            raise serializers.ValidationError(
                "У полезной привычки должно быть либо вознаграждение, либо связанная причина."
            )


class RelatedHabitValidator(HabitValidator):
    """Проверяет:
    - отсутствие ссылки объекта на самого себя по полю связанного ключа;
    - наличие у связанной привычки признака приятной привычки;
    - отсутствие связей у приятной привычки с полезными привычками при замене атрибута приятности на False."""

    def __call__(self, attrs):
        related_habit = self.get_attribute(attrs, "related_habit")

        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError("В поле связанная привычка можно указывать только приятную привычку.")
        if related_habit and related_habit not in Habit.objects.filter(user=self.user):
            raise serializers.ValidationError("В поле связанная привычка можно указывать только свои привычки.")
        if related_habit and related_habit == self.habit:
            raise serializers.ValidationError("В поле связанная привычка нельзя указывать ту же самую привычку.")
        if self.method != "POST" and "is_pleasant" in attrs:
            if self.habit.is_pleasant:
                related_useful_habits = Habit.objects.filter(related_habit=self.habit)
                if related_useful_habits:
                    related_useful_habits_pks = [habit.pk for habit in related_useful_habits]
                    raise serializers.ValidationError(
                        f"На данную привычку, как на приятную,"
                        f"ссылаются полезные привычки id={related_useful_habits_pks}."
                        f"Перед изменением признака 'приятный' необходимо исправить эти ссылки."
                    )
