from django.contrib import admin

from habits.models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "place",
        "action",
        "time",
        "duration",
        "periodicity",
        "is_pleasant",
        "award",
        "related_habit",
        "public_flag",
        "last_execution_datetime",
        "next_execution_datetime",
    ]
