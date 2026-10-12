from django.utils import timezone
from rest_framework import serializers
from ..models import Task
from .subtasks import SubTaskSerializer


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'deadline',
                  'created_at', 'owner')
        read_only_fields = ('id', 'created_at', 'owner')


class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)
    owner = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'deadline', 'created_at', 'subtasks', 'owner')
        read_only_fields = ('created_at', 'owner')


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        # owner будет добавлен в perform_create
        fields = ('id', 'title', 'description', 'status', 'deadline', 'created_at', 'owner')
        read_only_fields = ('id', 'created_at', 'owner')

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError('Deadline cannot be in the past.')
        return value
