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
            RelatedHabitValidator(habit),
        ]

    class Meta:
        model = Habit
        fields = "__all__"
