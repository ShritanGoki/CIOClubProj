from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'field_of_study', 'graduation_year', 'created_at')
    list_filter = ('role', 'field_of_study')
    search_fields = ('user__username', 'user__email')
    list_editable = ('role',)
