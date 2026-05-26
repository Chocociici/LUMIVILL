import asyncio
import websockets
import json
import base64
import os
import re
from datetime import datetime
from random import choice

connected = {}
users = {}
user_roles = {'ANGELINA': 'admin', 'admin': 'admin', 'Добрая Вискаша': 'bot'}
message_history = []
MAX_HISTORY = 200
unread_messages = {}
notification_history = []

BOT_PHRASES = [
    '🌸 Добро пожаловать, {name}! ✨',
    '🤗 Привет, {name}! Как настроение? 💖',
    '🫂 Ооо, {name} зашёл! 🎉',
]

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'app0', 'app0', 'static', 'chat', 'uploads')
os.makedirs(STATIC_DIR, exist_ok=True)

def save_to_history(msg):
    global message_history
    msg['id'] = len(message_history)
    message_history.append(msg)
    if len(message_history) > MAX_HISTORY:
        message_history.pop(0)

def add_notification(username, notification):
    if username not in notification_history:
        notification_history.append({'username': username, 'notifications': []})
    for user_notif in notification_history:
        if user_notif['username'] == username:
            user_notif['notifications'].insert(0, notification)
            if len(user_notif['notifications']) > 50:
                user_notif['notifications'].pop()
            break

def increment_unread(username, from_user, msg_preview=''):
    if username not in unread_messages:
        unread_messages[username] = {}
    unread_messages[username][from_user] = unread_messages[username].get(from_user, 0) + 1
    if username in connected:
        asyncio.create_task(connected[username].send(json.dumps({
            'type': 'unread_update',
            'unread': unread_messages[username]
        })))

def mark_as_read(username, from_user):
    if username in unread_messages and from_user in unread_messages[username]:
        del unread_messages[username][from_user]
        if username in connected:
            asyncio.create_task(connected[username].send(json.dumps({
                'type': 'unread_update',
                'unread': unread_messages[username]
            })))

async def handler(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            
            if data['type'] == 'join':
                username = data['username']
                is_staff = data.get('isStaff', False)
                role = 'admin' if is_staff or username in user_roles else 'user'
                users[username] = {'ws': websocket, 'role': role}
                connected[username] = websocket
                
                await websocket.send(json.dumps({
                    'type': 'history',
                    'messages': message_history
                }))
                
                if username in unread_messages:
                    await websocket.send(json.dumps({
                        'type': 'unread_update',
                        'unread': unread_messages[username]
                    }))
                
                for notif in notification_history:
                    if notif['username'] == username:
                        await websocket.send(json.dumps({
                            'type': 'notification_history',
                            'notifications': notif['notifications']
                        }))
                        break
                
                await broadcast_users()
                await broadcast_system(f'✨ {username} присоединился к чату ✨')
                
                await asyncio.sleep(0.5)
                bot_msg = choice(BOT_PHRASES).replace('{name}', username)
                save_to_history({
                    'type': 'bot',
                    'username': 'Добрая Вискаша',
                    'text': bot_msg,
                    'timestamp': datetime.now().isoformat(),
                    'role': 'bot'
                })
                await broadcast_bot(bot_msg)
            
            elif data['type'] == 'message':
                username = data['username']
                role = users.get(username, {}).get('role', 'user')
                text = data['text']
                
                mentioned_users = re.findall(r'@(\w+)', text)
                valid_mentions = [u for u in mentioned_users if u in connected and u != username]
                
                msg = {
                    'type': 'message',
                    'username': username,
                    'text': text,
                    'timestamp': datetime.now().isoformat(),
                    'role': role,
                    'mentions': valid_mentions
                }
                save_to_history(msg)
                await broadcast(msg)
                
                for mention in valid_mentions:
                    if mention in connected:
                        increment_unread(mention, username)
                        notification = {
                            'id': len(notification_history),
                            'type': 'mention',
                            'from': username,
                            'text': text[:100],
                            'timestamp': datetime.now().isoformat(),
                            'is_read': False
                        }
                        add_notification(mention, notification)
                        await connected[mention].send(json.dumps({
                            'type': 'mention_notify',
                            'from': username,
                            'text': text,
                            'timestamp': datetime.now().isoformat()
                        }))
                        await connected[mention].send(json.dumps({
                            'type': 'new_notification',
                            'notification': notification
                        }))
            
            elif data['type'] == 'mark_read':
                username = data['username']
                from_user = data['from_user']
                mark_as_read(username, from_user)
            
            elif data['type'] == 'mark_notification_read':
                username = data['username']
                notification_id = data['notification_id']
                for user_notif in notification_history:
                    if user_notif['username'] == username:
                        for n in user_notif['notifications']:
                            if n.get('id') == notification_id:
                                n['is_read'] = True
                                break
                        break
            
            elif data['type'] == 'private':
                to_user = data['to']
                from_user = data['from']
                text = data['text']
                
                if to_user in connected:
                    private_msg = {
                        'type': 'private',
                        'from': from_user,
                        'to': to_user,
                        'text': text,
                        'timestamp': datetime.now().isoformat()
                    }
                    save_to_history(private_msg)
                    
                    await connected[to_user].send(json.dumps({
                        'type': 'private',
                        'from': from_user,
                        'text': text,
                        'timestamp': datetime.now().isoformat()
                    }))
                    await connected[from_user].send(json.dumps({
                        'type': 'private',
                        'from': f'Вы -> {to_user}',
                        'text': text,
                        'timestamp': datetime.now().isoformat()
                    }))
                    
                    if to_user != from_user:
                        increment_unread(to_user, from_user)
                        notification = {
                            'id': len(notification_history),
                            'type': 'private',
                            'from': from_user,
                            'text': text[:100],
                            'timestamp': datetime.now().isoformat(),
                            'is_read': False
                        }
                        add_notification(to_user, notification)
                        await connected[to_user].send(json.dumps({
                            'type': 'new_notification',
                            'notification': notification
                        }))
            
            elif data['type'] == 'mention':
                from_user = data['from']
                targets = data['targets']
                text = data['text']
                
                mention_text = f"@{' @'.join(targets)}: {text}"
                msg = {
                    'type': 'message',
                    'username': from_user,
                    'text': mention_text,
                    'timestamp': datetime.now().isoformat(),
                    'role': users.get(from_user, {}).get('role', 'user'),
                    'mentions': targets
                }
                save_to_history(msg)
                await broadcast(msg)
                
                for target in targets:
                    if target in connected and target != from_user:
                        increment_unread(target, from_user)
                        notification = {
                            'id': len(notification_history),
                            'type': 'mention',
                            'from': from_user,
                            'text': text[:100],
                            'timestamp': datetime.now().isoformat(),
                            'is_read': False
                        }
                        add_notification(target, notification)
                        await connected[target].send(json.dumps({
                            'type': 'mention_notify',
                            'from': from_user,
                            'text': text,
                            'timestamp': datetime.now().isoformat()
                        }))
                        await connected[target].send(json.dumps({
                            'type': 'new_notification',
                            'notification': notification
                        }))
            
            elif data['type'] == 'admin_action':
                admin = data['admin']
                if users.get(admin, {}).get('role') != 'admin':
                    continue
                
                action = data['action']
                target = data['target']
                
                if action == 'ban':
                    if target in users:
                        users[target]['role'] = 'banned'
                        if target in connected:
                            await connected[target].send(json.dumps({
                                'type': 'system',
                                'text': '⛔ Вы забанены'
                            }))
                        await broadcast_system(f'👑 {admin} забанил {target}')
                elif action == 'unban':
                    if target in users:
                        users[target]['role'] = 'user'
                        await broadcast_system(f'👑 {admin} разбанил {target}')
                elif action == 'set_role':
                    if target in users:
                        users[target]['role'] = data['role']
                        await broadcast_system(f'👑 {admin} изменил роль {target}')
                
                await broadcast_users()
            
            elif data['type'] in ['image', 'audio']:
                username = data['username']
                role = users.get(username, {}).get('role', 'user')
                file_data = base64.b64decode(data['data'].split(',')[1])
                ext = 'png' if data['type'] == 'image' else 'mp3'
                filename = f"{datetime.now().timestamp()}_{username}.{ext}"
                filepath = os.path.join(STATIC_DIR, filename)
                with open(filepath, 'wb') as f:
                    f.write(file_data)
                
                url = f'/static/chat/uploads/{filename}'
                msg = {
                    'type': data['type'],
                    'username': username,
                    'url': url,
                    'timestamp': datetime.now().isoformat(),
                    'role': role
                }
                save_to_history(msg)
                await broadcast(msg)
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        for name, ws in list(connected.items()):
            if ws == websocket:
                del connected[name]
                await broadcast_system(f'👋 {name} покинул чат 👋')
                await broadcast_users()
                break

async def broadcast(msg, exclude=None):
    for name, ws in connected.items():
        if name != exclude:
            try:
                await ws.send(json.dumps(msg))
            except:
                pass

async def broadcast_system(text):
    await broadcast({'type': 'system', 'text': text})

async def broadcast_bot(text):
    await broadcast({
        'type': 'bot',
        'username': 'Добрая Вискаша',
        'text': text,
        'timestamp': datetime.now().isoformat(),
        'role': 'bot'
    })

async def broadcast_users():
    users_list = [{'username': u, 'role': users[u]['role']} for u in connected]
    await broadcast({'type': 'users', 'users': users_list})

async def main():
    port = int(os.environ.get('PORT', os.environ.get('CHAT_PORT', 3001)))
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"✅ Чат сервер запущен на порту {port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())