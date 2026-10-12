from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Task, Statuses

# pre_save, чтобы можно было взять старый статус и сравнить с новым
@receiver(pre_save, sender=Task)
def notify_task_status_change(sender, instance, **kwargs):

    # без отправки, если новая задача
    if instance.pk is None:
        return

    # без отправки, если нет владельца/почты (в теории быть должны, но на всякий случай)
    if not instance.owner or not instance.owner.email:
        return

    try:
        old = Task.objects.get(pk=instance.pk)
    except Task.DoesNotExist:
        return

    if old.status == instance.status:
        return

    owner_email = instance.owner.email

    if instance.status == Statuses.DONE:
        subject = f'Задача закрыта: {instance.title}'
        message = (
            f'Задача "{instance.title}" переведена в статус DONE.\n'
            f'Прошлый статус: {old.status}'
            f'Новый статус: {instance.status}'
            f'Дедлайн: {instance.deadline}'
        )
    else:
        subject = f'Задача изменена: {instance.title}'
        message = (
            f'Задача "{instance.title}" сменила статус.\n'
            f'Была: {old.status}'
            f'Стала: {instance.status}'
            f'Дедлайн: {instance.deadline}'
        )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[owner_email],
        fail_silently=True,
    )