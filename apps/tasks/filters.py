import django_filters
from .models import Task, SubTask


class TaskFilter(django_filters.FilterSet):
    deadline = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Task
        fields = ['status', 'deadline']


class SubTaskFilter(django_filters.FilterSet):
    deadline = django_filters.DateFromToRangeFilter()
    task_title = django_filters.CharFilter(field_name='task__title', lookup_expr='exact')

    class Meta:
        model = SubTask
        fields = ['status', 'deadline']