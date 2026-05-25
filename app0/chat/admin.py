from django.contrib import admin
from .models import ChatBan, UserChatSettings

@admin.register(ChatBan)
class ChatBanAdmin(admin.ModelAdmin):
    list_display = ('user', 'banned_by', 'reason', 'banned_at', 'expires_at')
    search_fields = ('user__username',)

@admin.register(UserChatSettings)
class UserChatSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'sound_enabled', 'theme')
    search_fields = ('user__username',)