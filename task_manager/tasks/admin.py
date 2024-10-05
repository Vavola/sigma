from django.contrib import admin
from .models import Task, Comment

admin.site.register(Task)
admin.site.register(Comment)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'deadline', 'created_by')
    search_fields = ('title', 'description')
    list_filter = ('status', 'priority', 'deadline')