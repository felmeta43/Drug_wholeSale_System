from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save, post_save, post_delete

from .middleware import get_current_user

# Fields that change on every save regardless of user intent, or that hold
# sensitive data — never worth (or safe) to surface in a diff.
IGNORED_FIELDS = {'updated_at', 'created_at', 'password', 'last_login'}


def _diff(old, new):
    changes = {}
    for field in new._meta.fields:
        if field.name in IGNORED_FIELDS:
            continue
        old_val = getattr(old, field.attname, None)
        new_val = getattr(new, field.attname, None)
        if old_val != new_val:
            changes[field.name] = [str(old_val), str(new_val)]
    return changes


def _audit_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._audit_old = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._audit_old = None
    else:
        instance._audit_old = None


def _audit_post_save(sender, instance, created, **kwargs):
    from .models import AuditLog
    content_type = ContentType.objects.get_for_model(sender)
    actor = get_current_user()
    if created:
        AuditLog.objects.create(
            actor=actor, action='create', content_type=content_type,
            object_id=instance.pk, object_repr=str(instance)[:255],
        )
        return
    old = getattr(instance, '_audit_old', None)
    if old is None:
        return
    changes = _diff(old, instance)
    if changes:
        AuditLog.objects.create(
            actor=actor, action='update', content_type=content_type,
            object_id=instance.pk, object_repr=str(instance)[:255], changes=changes,
        )


def _audit_post_delete(sender, instance, **kwargs):
    from .models import AuditLog
    AuditLog.objects.create(
        actor=get_current_user(), action='delete',
        content_type=ContentType.objects.get_for_model(sender),
        object_id=instance.pk, object_repr=str(instance)[:255],
    )


def register_audit(*models):
    """Wire up create/update/delete tracking for the given model classes."""
    for model in models:
        pre_save.connect(_audit_pre_save, sender=model, weak=False)
        post_save.connect(_audit_post_save, sender=model, weak=False)
        post_delete.connect(_audit_post_delete, sender=model, weak=False)


def _log_auth_event(action):
    def handler(sender, request, user=None, credentials=None, **kwargs):
        from .models import AuditLog
        if action == 'login_failed':
            username = (credentials or {}).get('username', '')
            AuditLog.objects.create(action=action, object_repr=str(username)[:255])
        else:
            AuditLog.objects.create(actor=user, action=action, object_repr=str(user)[:255])
    return handler


def connect_auth_signals():
    user_logged_in.connect(_log_auth_event('login'), weak=False)
    user_logged_out.connect(_log_auth_event('logout'), weak=False)
    user_login_failed.connect(_log_auth_event('login_failed'), weak=False)
