from .models import Notification, Chat
from django.db.models import Q

def notification_context(request):
    if not request.user.is_authenticated:
        return {}

    user = request.user

    # Separate notifications
    # ✅ First filter, then slice
    alerts = Notification.objects.filter(user=user, is_read=False).order_by('-timestamp')
    unread_count = alerts.count()
    alerts = alerts[:10]  # slice after count

    # Inbox chat messages
    chat_messages = Chat.objects.filter(
        Q(sender=user) | Q(thrift__user=user)
    ).order_by('-timestamp')[:10]

    return {
        'alerts': alerts,
        'unread_count': unread_count,
        'chat_messages': chat_messages,
    }
