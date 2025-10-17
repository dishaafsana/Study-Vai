from django.contrib import admin
from .models import Routine


class RoutineAdmin(admin.ModelAdmin):
    list_display = ("day", "time_slot", "Group_code", "Group_name")
    list_filter = ("day", "time_slot")
    search_fields = ("Group_code", "Group_name")


admin.site.register(Routine, RoutineAdmin)
