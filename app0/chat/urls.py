from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_page, name='chat_page'),
    path('api/chat/users/', views.get_users_list, name='chat_users'),
    path('api/chat/settings/', views.user_settings, name='chat_settings'),
    path('api/chat/profile/<str:username>/', views.get_user_profile, name='chat_profile'),
    path('api/chat/admin-action/', views.admin_action, name='chat_admin_action'),
]