from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ChatBan, UserChatSettings
from django.contrib.auth.models import User
import json

@login_required
def chat_page(request):
    is_banned = ChatBan.objects.filter(user=request.user).exists()
    
    # Создаём настройки, если их нет
    settings, _ = UserChatSettings.objects.get_or_create(user=request.user)
    
    return render(request, 'chat.html', {
        'is_banned': is_banned,
        'user': request.user
    })

@login_required
def get_users_list(request):
    """Получение списка всех пользователей"""
    users = User.objects.exclude(id=request.user.id).values('id', 'username', 'is_staff')
    return JsonResponse(list(users), safe=False)

@login_required
@csrf_exempt
@require_http_methods(["GET", "POST"])
def user_settings(request):
    """Получение и сохранение настроек пользователя"""
    settings, _ = UserChatSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if 'sound_enabled' in data:
                settings.sound_enabled = data['sound_enabled']
            if 'theme' in data:
                settings.theme = data['theme']
            settings.save()
            return JsonResponse({'status': 'ok', 'message': 'Настройки сохранены'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    # GET запрос
    return JsonResponse({
        'sound_enabled': settings.sound_enabled,
        'theme': settings.theme
    })

@login_required
def get_user_profile(request, username):
    """Получение профиля пользователя для модального окна"""
    try:
        target_user = User.objects.get(username=username)
        
        # Проверяем статус бана
        is_banned = ChatBan.objects.filter(user=target_user).exists()
        
        # Проверяем онлайн статус (опционально, можно добавить логику через WebSocket)
        is_online = False  # Здесь можно добавить проверку через connected словарь из WebSocket сервера
        
        return JsonResponse({
            'username': target_user.username,
            'is_staff': target_user.is_staff,
            'is_online': is_online,
            'is_banned': is_banned,
            'avatar_url': '/static/default-avatar.png',  # Замените на реальный URL аватара
            'profile_url': f'/profile/{target_user.username}/'  # Ссылка на страницу профиля
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def admin_action(request):
    """Административные действия (бан, разбан, изменение роли)"""
    # Проверяем, является ли пользователь админом
    if not request.user.is_staff:
        return JsonResponse({'error': 'Недостаточно прав'}, status=403)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        target_username = data.get('target')
        role = data.get('role')
        
        if not action or not target_username:
            return JsonResponse({'error': 'Не указаны обязательные параметры'}, status=400)
        
        target_user = get_object_or_404(User, username=target_username)
        
        # Запрещаем действия над самим собой
        if target_user.id == request.user.id:
            return JsonResponse({'error': 'Нельзя выполнять действия над собой'}, status=400)
        
        if action == 'ban':
            # Баним пользователя
            ban, created = ChatBan.objects.get_or_create(user=target_user)
            if created:
                return JsonResponse({'status': 'ok', 'message': f'Пользователь {target_username} забанен'})
            else:
                return JsonResponse({'status': 'ok', 'message': f'Пользователь {target_username} уже забанен'})
        
        elif action == 'unban':
            # Разбаниваем
            deleted, _ = ChatBan.objects.filter(user=target_user).delete()
            if deleted:
                return JsonResponse({'status': 'ok', 'message': f'Пользователь {target_username} разбанен'})
            else:
                return JsonResponse({'status': 'ok', 'message': f'Пользователь {target_username} не был забанен'})
        
        elif action == 'set_role':
            # Изменяем роль (только для staff)
            if role == 'admin':
                target_user.is_staff = True
                target_user.save()
                return JsonResponse({'status': 'ok', 'message': f'Пользователь {target_username} повышен до администратора'})
            elif role == 'user':
                target_user.is_staff = False
                target_user.save()
                return JsonResponse({'status': 'ok', 'message': f'Пользователь {target_username} понижен до обычного пользователя'})
            else:
                return JsonResponse({'error': 'Неверная роль'}, status=400)
        
        else:
            return JsonResponse({'error': 'Неизвестное действие'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)