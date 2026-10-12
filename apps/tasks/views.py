from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .filters import TaskFilter, SubTaskFilter
from .models import Task, Statuses, SubTask, Category
from .serializers.tasks import TaskSerializer, TaskCreateSerializer, TaskDetailSerializer
from .serializers.subtasks import SubTaskCreateSerializer, SubTaskSerializer
from .serializers.categories import CategorySerializer
# from .paginators.subtask import SubTaskPagination


# @api_view(['POST'])
# def task_create(request):
#     serializer = TaskSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
# @api_view(['GET'])
# def task_list(request):
#     tasks = Task.objects.all()
#
#     weekday = request.query_params.get('weekday')
#     if weekday:
#         weekday_map = {
#             'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
#             'friday': 4, 'saturday': 5, 'sunday': 6,
#         }
#         day_num = weekday_map.get(weekday.lower())
#         if day_num is not None:
#             tasks = tasks.filter(deadline__week_day=(day_num + 2) % 7)
#
#     serializer = TaskSerializer(tasks, many=True)
#     return Response(serializer.data)
#
#
# @api_view(['GET'])
# def task_detail(request, pk):
#     task = get_object_or_404(Task, pk=pk)
#     serializer = TaskSerializer(task)
#     return Response(serializer.data)


# class SubTaskListCreateView(APIView):
#     def get(self, request):
#         subtasks = SubTask.objects.all().order_by('-created_at')
#
#         task_title = request.query_params.get('task_title')
#         if task_title:
#             subtasks = subtasks.filter(task__title=task_title)
#
#         status_param = request.query_params.get('status')
#         if status_param:
#             subtasks = subtasks.filter(status=status_param)
#
#         paginator = SubTaskPagination()
#         page = paginator.paginate_queryset(subtasks, request, view=self)
#         serializer = SubTaskSerializer(page, many=True)
#         return paginator.get_paginated_response(serializer.data)
#
#     def post(self, request):
#         serializer = SubTaskCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class SubTaskDetailUpdateDeleteView(APIView):
#     def get_object(self, pk):
#         return get_object_or_404(SubTask, pk=pk)
#
#     def get(self, request, pk):
#         subtask = self.get_object(pk)
#         serializer = SubTaskSerializer(subtask)
#         return Response(serializer.data)
#
#     def put(self, request, pk):
#         subtask = self.get_object(pk)
#         serializer = SubTaskCreateSerializer(subtask, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def patch(self, request, pk):
#         subtask = self.get_object(pk)
#         serializer = SubTaskCreateSerializer(subtask, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         subtask = self.get_object(pk)
#         subtask.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def task_stats(request):
    now = timezone.now()
    total = Task.objects.count()
    by_status = Task.objects.values('status').annotate(count=Count('id')).order_by('status')

    # для отображения полного списка статусов, даже если нет соответствующих задач
    status_counts = {item['status']: item['count'] for item in by_status}
    for choice in Statuses:
        status_counts.setdefault(choice.value, 0)

    overdue = Task.objects.filter(deadline__lt=now).exclude(status=Statuses.DONE).count()
    return Response({
        'total': total,
        'by_status': status_counts,
        'overdue': overdue,
    })


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TaskDetailSerializer
        return TaskCreateSerializer


class SubTaskListCreateView(generics.ListCreateAPIView):
    queryset = SubTask.objects.all()
    # pagination_class = SubTaskPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SubTaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubTaskCreateSerializer
        return SubTaskSerializer


class SubTaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SubTaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SubTaskSerializer
        return SubTaskCreateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=False, methods=['get'], url_path='count-tasks')
    def count_tasks(self, request):
        categories = (
            Category.objects
            .annotate(tasks_count=Count('tasks'))
            .values('id', 'name', 'tasks_count')
        )
        return Response(list(categories))
