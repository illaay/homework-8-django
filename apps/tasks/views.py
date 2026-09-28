from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Task, Statuses
from .serializers.tasks import TaskSerializer


@api_view(['POST'])
def task_create(request):
    serializer = TaskSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def task_list(request):
    tasks = Task.objects.all()
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
