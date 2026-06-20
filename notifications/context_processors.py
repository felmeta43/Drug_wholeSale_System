def notifications(request):
    if not request.user.is_authenticated:
        return {}
    qs = request.user.notifications.filter(is_read=False)[:10]
    return {
        'unread_notifications': qs,
        'unread_notification_count': request.user.notifications.filter(is_read=False).count(),
    }
