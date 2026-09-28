from django.contrib import admin, messages
from django.utils.translation import ngettext
from .models import Task, SubTask, Category, Statuses


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1
    readonly_fields = ('created_at',)
    show_change_link = True


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('short_title', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'created_at', 'deadline')
    search_fields = ('title', 'description')
    filter_horizontal = ('categories',)
    inlines = [SubTaskInline]

    @admin.display(description='Title', ordering='title')
    def short_title(self, obj):
        if len(obj.title) > 10:
            return f"{obj.title[:10]}..."
        return obj.title


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'task', 'deadline')
    search_fields = ('title', 'description')
    actions = ['mark_as_done']

    @admin.action(description='Mark selected subtasks as Done')
    def mark_as_done(self, request, queryset):
        updated = queryset.update(status=Statuses.DONE)
        self.message_user(
            request,
            ngettext(
                '%d subtask was successfully marked as Done.',
                '%d subtasks were successfully marked as Done.',
                updated,
            ) % updated,
            messages.SUCCESS,
        )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
