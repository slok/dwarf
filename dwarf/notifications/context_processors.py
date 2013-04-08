from django.conf import settings


def push_notifications_context_processor(request):
    return {
        'push_notifications_server_url': settings.PUSH_NOTIFICATIONS_SERVER_URL
    }
