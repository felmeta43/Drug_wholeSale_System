import threading

_thread_locals = threading.local()


def get_current_user():
    return getattr(_thread_locals, 'user', None)


class CurrentUserMiddleware:
    """Stashes the logged-in user in a thread-local so model signal handlers
    (which have no access to the request) can attribute changes to whoever
    made them — see core/signals.py."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        _thread_locals.user = user if user and user.is_authenticated else None
        try:
            response = self.get_response(request)
        finally:
            _thread_locals.user = None
        return response
