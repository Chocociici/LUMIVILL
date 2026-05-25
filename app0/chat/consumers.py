import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, ChatMessage, ChatBan
from django.utils import timezone
import random

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Проверка бана
        is_banned = await self.is_user_banned()
        if is_banned:
            await self.close()
            return
        
        self.room_group_name = 'chat_public'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # История сообщений
        messages = await self.get_recent_messages()
        await self.send(text_data=json.dumps({
            'type': 'history',
            'messages': messages
        }))
        
        # Приветствие бота
        await self.bot_greeting()
        
        # Оповещаем всех о новом пользователе
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'username': self.user.username,
                'user_id': self.user.id
            }
        )
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_leave',
                'username': self.user.username,
                'user_id': self.user.id
            }
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')
        
        if msg_type == 'message':
            text = data.get('text', '')
            if not text.strip():
                return
            
            # Сохраняем сообщение
            message = await self.save_message(text)
            
            # Проверка на упоминание
            mentioned = False
            if f'@{self.user.username}' in text:
                mentioned = True
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'id': message['id'],
                    'username': self.user.username,
                    'user_id': self.user.id,
                    'text': text,
                    'timestamp': message['timestamp'],
                    'mentioned': mentioned,
                    'mentioned_by': self.user.username if mentioned else None
                }
            )
        
        elif msg_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'username': self.user.username
                }
            )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'id': event['id'],
            'username': event['username'],
            'user_id': event['user_id'],
            'text': event['text'],
            'timestamp': event['timestamp'],
            'mentioned': event.get('mentioned', False),
            'mentioned_by': event.get('mentioned_by')
        }))
    
    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': event['username']
        }))
    
    async def user_join(self, event):
        await self.send(text_data=json.dumps({
            'type': 'system',
            'text': f'✨ {event["username"]} присоединился к чату ✨'
        }))
    
    async def user_leave(self, event):
        await self.send(text_data=json.dumps({
            'type': 'system',
            'text': f'👋 {event["username"]} покинул чат 👋'
        }))
    
    async def bot_greeting(self):
        greetings = [
            f'🌸 Добро пожаловать, {self.user.username}! Рада тебя видеть! ✨',
            f'🤗 Привет, {self.user.username}! Как настроение? 💖',
            f'🫂 Ооо, {self.user.username} зашёл! Будет весело! 🎉',
            f'💫 С возвращением, {self.user.username}! Скучали! 🌟'
        ]
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': 0,
                'username': 'Добрая Вискаша',
                'user_id': 0,
                'text': random.choice(greetings),
                'timestamp': timezone.now().isoformat(),
                'mentioned': False
            }
        )
    
    @database_sync_to_async
    def is_user_banned(self):
        ban = ChatBan.objects.filter(user=self.user).first()
        if ban and (ban.expires_at is None or ban.expires_at > timezone.now()):
            return True
        return False
    
    @database_sync_to_async
    def get_recent_messages(self):
        room, _ = ChatRoom.objects.get_or_create(room_type='public', defaults={'name': 'Общий чат'})
        messages = ChatMessage.objects.filter(room=room, is_deleted=False).order_by('-created_at')[:50]
        return [{
            'id': m.id,
            'username': m.sender.username,
            'user_id': m.sender.id,
            'text': m.text,
            'timestamp': m.created_at.isoformat()
        } for m in reversed(messages)]
    
    @database_sync_to_async
    def save_message(self, text):
        room, _ = ChatRoom.objects.get_or_create(room_type='public', defaults={'name': 'Общий чат'})
        message = ChatMessage.objects.create(
            room=room,
            sender=self.user,
            text=text
        )
        return {
            'id': message.id,
            'timestamp': message.created_at.isoformat()
        }