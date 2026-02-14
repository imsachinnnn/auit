from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import BonafideRequest, LeaveRequest
from webpush import send_user_notification

@receiver(pre_save, sender=BonafideRequest)
def store_previous_status_bonafide(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = BonafideRequest.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except BonafideRequest.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=BonafideRequest)
def notify_bonafide_status_change(sender, instance, created, **kwargs):
    if created:
        return # Don't notify on creation (usually pending)
    
    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status
    
    if old_status != new_status:
        user = instance.student.user
        if not user:
            return

        payload = {
            "head": "Bonafide Request Update",
            "body": f"Your request status has changed to: {new_status}",
            "icon": "/static/imgs/annamalai.png",
            "url": "/student/bonafide/" # Adjust URL as needed
        }
        
        try:
            send_user_notification(user=user, payload=payload, ttl=1000)
        except Exception as e:
            print(f"Failed to send push notification: {e}")

@receiver(pre_save, sender=LeaveRequest)
def store_previous_status_leave(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = LeaveRequest.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except LeaveRequest.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=LeaveRequest)
def notify_leave_status_change(sender, instance, created, **kwargs):
    if created:
        return

    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status

    if old_status != new_status:
        user = instance.student.user
        if not user:
            return

        payload = {
            "head": "Leave Request Update",
            "body": f"Your leave request status is now: {new_status}",
            "icon": "/static/imgs/annamalai.png",
            "url": "/student/leave/history/" 
        }

        try:
            send_user_notification(user=user, payload=payload, ttl=1000)
        except Exception as e:
            print(f"Failed to send push notification: {e}")
