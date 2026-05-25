from .models import ChatBan
from django.utils import timezone

def is_user_banned(user):
    ban = ChatBan.objects.filter(user=user).first()
    if ban and (ban.expires_at is None or ban.expires_at > timezone.now()):
        return True
    return False