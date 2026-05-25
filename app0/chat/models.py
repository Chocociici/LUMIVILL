from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ChatRoom(models.Model):
    ROOM_TYPES = [
        ('public', 'Публичный чат'),
        ('private', 'Приватный чат'),
    ]
    
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='public')
    name = models.CharField(max_length=100, blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='chat_rooms', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.room_type == 'public':
            return 'Общий чат'
        return f"ЛС: {', '.join([u.username for u in self.participants.all()])}"
    
    class Meta:
        ordering = ['-updated_at']

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.text[:50]}"

class ChatAttachment(models.Model):
    ATTACHMENT_TYPES = [
        ('image', 'Изображение'),
        ('audio', 'Аудио'),
        ('file', 'Файл'),
    ]
    
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='chat_attachments/%Y/%m/%d/')
    attachment_type = models.CharField(max_length=10, choices=ATTACHMENT_TYPES)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class UserChatSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chat_settings')
    sound_enabled = models.BooleanField(default=True)
    sound_volume = models.IntegerField(default=30)
    theme = models.CharField(max_length=20, default='dark')
    enter_sound = models.CharField(max_length=100, blank=True)
    message_sound = models.CharField(max_length=100, blank=True)
    mention_sound = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Настройки чата для {self.user.username}"

class ChatBan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chat_ban')
    banned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_bans')
    reason = models.TextField()
    banned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} забанен до {self.expires_at}"