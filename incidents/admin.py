from django.contrib import admin
from .models import Incident


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("inc_id", "date", "incident_type", "status", "responsible", "is_active")
    list_filter = ("incident_type", "status", "is_active")
    search_fields = ("description", "responsible")
    ordering = ("-date", "-inc_id")
