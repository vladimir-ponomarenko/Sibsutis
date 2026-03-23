from django.contrib import admin

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_by", "created_at", "views")
    search_fields = ("title", "uploaded_by__username")
