from django.urls import path
from .views import task_create, task_list, task_detail, task_stats, SubTaskListCreateView, SubTaskDetailUpdateDeleteView

urlpatterns = [
    path('tasks/create/', task_create, name='task-create'),
    path('tasks/list/', task_list, name='task-list'),
    path('tasks/<int:pk>/', task_detail, name='task-detail'),
    path('tasks/stats/', task_stats, name='task-stats'),
    path('subtasks/', SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('subtasks/<int:pk>/', SubTaskDetailUpdateDeleteView.as_view(), name='subtask-detail'),
]