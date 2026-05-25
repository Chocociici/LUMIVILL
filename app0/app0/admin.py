from django.contrib import admin
from django.utils.html import format_html
from .models import News, Event, Character, CharacterImage, Comment, UserProfile
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms

class NewsAdminForm(forms.ModelForm):
    full_text = forms.CharField(widget=CKEditorUploadingWidget())
    
    class Meta:
        model = News
        fields = '__all__'

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    list_display = ('title', 'date', 'is_published')
    list_filter = ('is_published', 'date')
    search_fields = ('title', 'short_description')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'is_published')
    list_filter = ('is_published', 'event_date')
    search_fields = ('title',)

class CharacterImageInline(admin.TabularInline):
    model = CharacterImage
    extra = 3

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'status_badge', 'created_at', 'admin_action_needed')
    list_filter = ('status', 'created_at', 'author')
    search_fields = ('name', 'author__username')
    inlines = [CharacterImageInline]
    
    fieldsets = (
        ('Статус', {
            'fields': ('status', 'admin_comment')
        }),
        ('Основная информация', {
            'fields': ('author', 'name', 'age', 'gender', 'race', 'height_weight', 'faction')
        }),
        ('Описание', {
            'fields': ('appearance', 'personality', 'occupation')
        }),
        ('Способности', {
            'fields': ('combat_skills', 'racial_abilities', 'magic', 'inventory', 'documents', 'weaknesses')
        }),
        ('Биография', {
            'fields': ('biography',)
        }),
        ('Медиа', {
            'fields': ('main_image', 'music', 'pony_town_skin', 'voice_file', 'art_file')
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': '#8B7355',
            'approved': '#DAA520',
            'declined': '#8B0000',
            'edited': '#FF8C00',
        }
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', colors.get(obj.status, '#666'), obj.get_status_display())
    status_badge.short_description = 'Статус'
    
    def admin_action_needed(self, obj):
        if obj.status == 'pending':
            return format_html('<span style="color: #FF8C00; font-weight: bold;">⚠️ ТРЕБУЕТ ПРОВЕРКИ!</span>')
        return '-'
    admin_action_needed.short_description = 'Действие'
    
    actions = ['approve_characters', 'decline_characters']
    
    def approve_characters(self, request, queryset):
        queryset.update(status='approved')
    approve_characters.short_description = 'Одобрить выбранные анкеты'
    
    def decline_characters(self, request, queryset):
        queryset.update(status='declined')
    decline_characters.short_description = 'Отклонить выбранные анкеты'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'character', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('author__username', 'character__name')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'reputation_badge_display', 'registration_date', 'has_bio')
    list_filter = ('reputation', 'registration_date')
    search_fields = ('user__username', 'bio', 'admin_note')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'avatar', 'bio', 'location')
        }),
        ('Контакты', {
            'fields': ('discord', 'telegram', 'website')
        }),
        ('Репутация и модерация', {
            'fields': ('reputation', 'admin_note'),
            'description': 'Управление репутацией пользователя. Заметки видны только администраторам.'
        }),
    )
    
    def reputation_badge_display(self, obj):
        return format_html(obj.get_reputation_badge())
    reputation_badge_display.short_description = 'Репутация'
    
    def has_bio(self, obj):
        return bool(obj.bio)
    has_bio.boolean = True
    has_bio.short_description = 'Заполнен профиль'