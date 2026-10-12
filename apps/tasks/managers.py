from django.db import models
from django.utils import timezone


class CategoryQuerySet(models.QuerySet):
    def delete(self):
        return super().update(is_deleted=True, deleted_at=timezone.now())

class CategoryManager(models.Manager.from_queryset(CategoryQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)