from django.contrib import admin
from .models import Event, Reminder


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'cio', 'event_type', 'start_time', 'is_public')
    list_filter = ('event_type', 'is_public')
    search_fields = ('title', 'cio__name')


admin.site.register(Reminder)
