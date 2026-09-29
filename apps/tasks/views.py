from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Task, Statuses, SubTask
from .serializers.tasks import TaskSerializer
from .serializers.subtasks import SubTaskCreateSerializer, SubTaskSerializer
from .paginators.subtask import SubTaskPagination


@api_view(['POST'])
def task_create(request):
    serializer = TaskSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def task_list(request):
    tasks = Task.objects.all()

    weekday = request.query_params.get('weekday')
    if weekday:
        weekday_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6,
        }
        day_num = weekday_map.get(weekday.lower())
        if day_num is not None:
            tasks = tasks.filter(deadline__week_day=(day_num + 2) % 7)

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    serializer = TaskSerializer(task)
    return Response(serializer.data)


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


class SubTaskListCreateView(APIView):
    def get(self, request):
        subtasks = SubTask.objects.all().order_by('-created_at')

        task_title = request.query_params.get('task_title')
        if task_title:
            subtasks = subtasks.filter(task__title=task_title)

        status_param = request.query_params.get('status')
        if status_param:
            subtasks = subtasks.filter(status=status_param)

        paginator = SubTaskPagination()
        page = paginator.paginate_queryset(subtasks, request, view=self)
        serializer = SubTaskSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubTaskDetailUpdateDeleteView(APIView):
    def get_object(self, pk):
        return get_object_or_404(SubTask, pk=pk)

    def get(self, request, pk):
        subtask = self.get_object(pk)
        serializer = SubTaskSerializer(subtask)
        return Response(serializer.data)

    def put(self, request, pk):
        subtask = self.get_object(pk)
        serializer = SubTaskCreateSerializer(subtask, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        subtask = self.get_object(pk)
        serializer = SubTaskCreateSerializer(subtask, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        subtask = self.get_object(pk)
        subtask.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
