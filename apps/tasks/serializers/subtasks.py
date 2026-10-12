from rest_framework import serializers
from ..models import SubTask


class SubTaskSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = SubTask
        fields = ('id', 'title', 'description', 'task', 'status',
                  'deadline', 'created_at', 'owner')
        read_only_fields = ('id', 'created_at', 'owner')


class SubTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        # owner будет добавлен в perform_create
        fields = ('id', 'title', 'description', 'task', 'status',
                  'deadline', 'created_at', 'owner')
        read_only_fields = ('id', 'created_at', 'owner')
