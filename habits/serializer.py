from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import IntegerField

from habits.models import Habit
from habits.validators import (DurationValidator, PeriodicityValidator, PleasantOrUsefulHabitValidator,
                               RelatedHabitValidator)


class HabitSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    action = serializers.CharField()
    periodicity = IntegerField(allow_null=True)
    duration = serializers.DurationField()
    is_pleasant = serializers.BooleanField()
    related_habit = serializers.PrimaryKeyRelatedField(required=False, queryset=Habit.objects.none(), allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        habit = self.instance

        # возможность выбора у пользователя в качестве связанной привычки только своих привычек
        if request.method == "POST":
            self.fields["related_habit"].queryset = Habit.objects.filter(user=request.user)
        if request.method in ["PATCH", "PUT"]:
            self.fields["related_habit"].queryset = Habit.objects.filter(user=habit.user)

        self.validators = [
            DurationValidator(),
            PeriodicityValidator(),
            PleasantOrUsefulHabitValidator(),
            RelatedHabitValidator(habit, request.method),
        ]

    def next_execution_datetime_generation(self, instance):
        now_datetime = timezone.now()
        local_now = timezone.localtime(now_datetime)
        target_date = local_now.date()
        target_time = instance.time
        nearest_datetime = timezone.make_aware(
            timezone.datetime.combine(target_date, target_time), timezone.get_current_timezone()
        )
        if nearest_datetime <= now_datetime:
            target_date += timezone.timedelta(days=1)
            nearest_datetime = timezone.make_aware(
                timezone.datetime.combine(target_date, target_time), timezone.get_current_timezone()
            )

        instance.next_execution_time = nearest_datetime

    def create(self, validated_data):
        instance = super().create(validated_data)
        # self.user = self.context.get("request").user
        self.next_execution_datetime_generation(instance)
        return instance

    def update(self, instance, validated_data):
        self.next_execution_datetime_generation(instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ["last_execution_time", "next_execution_time"]
