from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app0 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('events/', views.EventListView.as_view(), name='events_list'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('catalog/', views.catalog, name='catalog'),
    path('characters/', views.catalog, name='characters_list'),
    path('character/<int:pk>/', views.character_detail, name='character_detail'),
    path('character/create/', views.create_character, name='create_character'),
    path('character/<int:pk>/edit/', views.edit_character, name='edit_character'),
    path('character/<int:pk>/delete/', views.delete_character, name='delete_character'),
    path('character/<int:character_id>/comment/', views.add_comment, name='add_comment'),
    path('chat/', include('app0.chat.urls')),  # ← ИСПРАВЛЕНО: было 'chat.urls'
    path('', include('app0.chat.urls')),       # ← ИСПРАВЛЕНО: было 'chat.urls'
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    
    path('admin-characters/', views.admin_character_list, name='admin_character_list'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)