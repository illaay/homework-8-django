from django.utils import timezone
from rest_framework import serializers
from ..models import Task
from .subtasks import SubTaskSerializer


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'deadline')


class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'deadline', 'created_at', 'subtasks')
        read_only_fields = ('created_at',)


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'deadline', 'created_at')
        read_only_fields = ('created_at',)

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError('Deadline cannot be in the past.')
        return value
