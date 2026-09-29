from rest_framework import serializers
from ..models import SubTask


class SubTaskCreateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubTask
        fields = ('id', 'title', 'description', 'task', 'status', 'deadline', 'created_at')


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ('id', 'title', 'description', 'status', 'deadline', 'created_at')
        read_only_fields = ('created_at',)
