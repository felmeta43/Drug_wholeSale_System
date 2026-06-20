def notify(recipient, message, link=''):
    """Create a notification for recipient. No-op if recipient is None
    (e.g. a Warehouse with no assigned manager)."""
    if recipient is None:
        return None
    from .models import Notification
    return Notification.objects.create(recipient=recipient, message=message, link=link)
