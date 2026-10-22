from django.contrib import admin
from .models import (
    Category, CIO, Officer, Bookmark, Application,
    Announcement, Review, CIODocument, CIOPhoto, ProfileView, GaugeInterest,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CIO)
class CIOAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'membership_type', 'applications_open', 'is_active')
    list_filter = ('category', 'membership_type', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_display = ('user', 'cio', 'role', 'is_primary')
    list_filter = ('role',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'cio', 'status', 'submitted_at')
    list_filter = ('status',)


admin.site.register(Bookmark)
admin.site.register(Announcement)
admin.site.register(Review)
admin.site.register(CIODocument)
admin.site.register(CIOPhoto)
admin.site.register(ProfileView)
admin.site.register(GaugeInterest)
