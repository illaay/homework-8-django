import os
import django
from datetime import timedelta


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangohw8.settings')
django.setup()


from django.utils import timezone
from apps.tasks.models import Task, SubTask, Statuses

#задание 1
def create_task():
    task = Task.objects.create(
        title="Prepare presentation",
        description="Prepare materials and slides for the presentation",
        status=Statuses.NEW,
        deadline=timezone.now() + timedelta(days=3),
    )
    print(f"Created task: {task}")
    return task


def create_subtasks(task):
    subtask1 = SubTask.objects.create(
        title="Gather information",
        description="Find necessary information for the presentation",
        status=Statuses.NEW,
        deadline=timezone.now() + timedelta(days=2),
        task=task,
    )
    print(f"Created subtask: {subtask1}")

    subtask2 = SubTask.objects.create(
        title="Create slides",
        description="Create presentation slides",
        status=Statuses.NEW,
        deadline=timezone.now() + timedelta(days=1),
        task=task,
    )
    print(f"Created subtask: {subtask2}")
    return subtask1, subtask2


# ----------
# задание 2
def show_new_tasks():
    print("\n--- Tasks with status 'New' ---")
    new_tasks = Task.objects.filter(status=Statuses.NEW)
    for task in new_tasks:
        print(f"Status: {task.status}, Title: {task.title}, Deadline: {task.deadline}")
    print(f"Total: {new_tasks.count()}")


def show_expired_done_subtasks():
    print("\n--- SubTasks with status 'Done' and expired deadline ---")
    expired_subtasks = SubTask.objects.filter(
        status=Statuses.DONE,
        deadline__lt=timezone.now(),
    )
    for subtask in expired_subtasks:
        print(f"Status: {subtask.status}, Title: {subtask.title}, Deadline: {subtask.deadline}")
    print(f"Total: {expired_subtasks.count()}")


# ----------
# задание 3
def update_records():
    updated = Task.objects.filter(title="Prepare presentation").update(status=Statuses.IN_PROGRESS)
    print(f"\nUpdated tasks (status -> In progress): {updated}")

    updated = SubTask.objects.filter(title="Gather information").update(
        deadline=timezone.now() - timedelta(days=2),
    )
    print(f"Updated subtasks (Gather information deadline -> -2 days): {updated}")

    updated = SubTask.objects.filter(title="Create slides").update(
        description="Create and format presentation slides",
    )
    print(f"Updated subtasks (Create slides description): {updated}")


# ----------
# задание 4
def delete_task_with_subtasks():
    try:
        task = Task.objects.get(title="Prepare presentation")
    except Task.DoesNotExist:
        print("\nTask 'Prepare presentation' not found, nothing to delete.")
        return

    subtasks_count = task.subtasks.count()
    task_title = task.title
    task.delete()
    print(f"\nDeleted task {task_title} and {subtasks_count} related subtask(s).")


if __name__ == '__main__':
    # задание 1
    task = create_task()
    create_subtasks(task)

    # задание 2
    show_new_tasks()
    show_expired_done_subtasks()

    # задание 3
    update_records()

    # задание 4
    delete_task_with_subtasks()
