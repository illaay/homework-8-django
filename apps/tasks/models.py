from django.db import models
from django.core.validators import MinLengthValidator


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Statuses(models.TextChoices):
    NEW = 'new', 'New'
    IN_PROGRESS = 'in_progress', 'In progress'
    PENDING = 'pending', 'Pending'
    BLOCKED = 'blocked', 'Blocked'
    DONE = 'done', 'Done'


class Task(TimeStampModel):

    title = models.CharField(max_length=25, validators=[MinLengthValidator(5)], verbose_name='Title',
                             unique_for_date='created_at')
    description = models.TextField(blank=True, default='')
    categories = models.ManyToManyField('Category', related_name='tasks')
    status = models.CharField(max_length=12, choices=Statuses)
    deadline = models.DateTimeField()


class SubTask(TimeStampModel):
    title = models.CharField(max_length=30, validators=[MinLengthValidator(5)])
    description = models.TextField(blank=True, default='')
    task = models.ForeignKey('Task', related_name='subtasks', on_delete=models.CASCADE)
    status = models.CharField(max_length=11, choices=Statuses)
    deadline = models.DateTimeField()


class Category(TimeStampModel):
    name = models.CharField(max_length=30, validators=[MinLengthValidator(3)])
