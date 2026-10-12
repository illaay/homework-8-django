from django.urls import path
# from .views import task_create, task_list, task_detail, task_stats, SubTaskListCreateView, SubTaskDetailUpdateDeleteView
from .views import (
    TaskListCreateView, TaskRetrieveUpdateDestroyView, task_stats,
    SubTaskListCreateView, SubTaskRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('tasks/stats/', task_stats, name='task-stats'),
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    # path('tasks/create/', TaskListCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
    path('subtasks/', SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('subtasks/<int:pk>/', SubTaskRetrieveUpdateDestroyView.as_view(), name='subtask-detail'),
]
