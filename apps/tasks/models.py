from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.conf import settings

from .managers import CategoryManager


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
    # null для совмести с имеющимися записями, чтобы заново сейчас не наполнять бд + для свободы в админке
    # в других моделях так же
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='tasks', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'task_manager_task'
        ordering = ['-created_at']
        verbose_name = 'Task'
        # либо unique=True в качестве аргумента в CharField
        constraints = [
            models.UniqueConstraint(fields=['title'], name='unique_task_title'),
        ]


class SubTask(TimeStampModel):
    title = models.CharField(max_length=30, validators=[MinLengthValidator(5)])
    description = models.TextField(blank=True, default='')
    task = models.ForeignKey('Task', related_name='subtasks', on_delete=models.CASCADE)
    status = models.CharField(max_length=11, choices=Statuses)
    deadline = models.DateTimeField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='subtasks', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'task_manager_subtask'
        ordering = ['-created_at']
        verbose_name = 'SubTask'
        constraints = [
            models.UniqueConstraint(fields=['title'], name='unique_subtask_title'),
        ]


class Category(TimeStampModel):
    name = models.CharField(max_length=30, validators=[MinLengthValidator(3)])
    # можно в виде property, но сделал, как сказано в условии
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = CategoryManager()
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'task_manager_category'
        verbose_name = 'Category'
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_category_name'),
        ]
