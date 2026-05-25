from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    short_description = models.CharField(max_length=120, verbose_name="Краткое описание (до 120 символов)")
    full_text = RichTextUploadingField(verbose_name="Полный текст")
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Изображение")
    date = models.DateTimeField(default=timezone.now, verbose_name="Дата публикации")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('news_detail', args=[self.id])

class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название ивента")
    short_description = models.CharField(max_length=120, verbose_name="Краткое описание")
    full_text = RichTextUploadingField(verbose_name="Полное описание")
    image = models.ImageField(upload_to='events/', blank=True, null=True, verbose_name="Изображение")
    event_date = models.DateTimeField(verbose_name="Дата проведения")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-event_date']
        verbose_name = "Ивент"
        verbose_name_plural = "Ивенты"
    
    def __str__(self):
        return self.title

class CharacterImage(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, related_name='character_images')
    image = models.ImageField(upload_to='characters/gallery/')
    title = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Изображение для {self.character.name}"

class Character(models.Model):
    STATUS_CHOICES = [
        ('pending', '⛧ Не проверено'),
        ('approved', '⚜ Одобрено'),
        ('declined', '☠ Не одобрено'),
        ('edited', '📝 Требует изменений'),
    ]
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='characters', verbose_name="Автор")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    admin_comment = models.TextField(blank=True, verbose_name="Комментарий администрации")
    
    # Основная информация (обязательная)
    name = models.CharField(max_length=200, verbose_name="Имя и фамилия, псевдоним")
    age = models.CharField(max_length=100, verbose_name="Возраст")
    gender = models.CharField(max_length=50, verbose_name="Пол")
    race = models.CharField(max_length=100, verbose_name="Раса")
    appearance = models.TextField(verbose_name="Особенности внешности")
    
    # Необязательные поля
    height_weight = models.CharField(max_length=100, blank=True, null=True, verbose_name="Рост и вес")
    faction = models.CharField(max_length=100, blank=True, null=True, verbose_name="Фракция")
    personality = models.TextField(blank=True, null=True, verbose_name="Характер")
    occupation = models.CharField(max_length=200, blank=True, null=True, verbose_name="Профессия/Роль")
    
    # Способности (необязательные)
    combat_skills = models.TextField(blank=True, null=True, verbose_name="Боевые навыки")
    racial_abilities = models.TextField(blank=True, null=True, verbose_name="Расовые способности")
    magic = RichTextUploadingField(blank=True, null=True, verbose_name="Магические способности")
    inventory = RichTextUploadingField(blank=True, null=True, verbose_name="Инвентарь")
    documents = models.TextField(blank=True, null=True, verbose_name="Документы")
    weaknesses = models.TextField(blank=True, null=True, verbose_name="Слабости")
    biography = RichTextUploadingField(blank=True, null=True, verbose_name="Биография")
    
    # Медиа (все необязательные)
    main_image = models.ImageField(upload_to='characters/main/', blank=True, null=True, verbose_name="Главное изображение")
    gallery = models.ManyToManyField(CharacterImage, blank=True, related_name='character_gallery', verbose_name="Галерея")
    music = models.FileField(upload_to='characters/music/', blank=True, null=True, verbose_name="Музыка (MP3)")
    pony_town_skin = models.ImageField(upload_to='characters/skins/', blank=True, null=True, verbose_name="Скин в Pony Town")
    voice_file = models.FileField(upload_to='characters/voice/', blank=True, null=True, verbose_name="Голос (аудио)")
    art_file = models.ImageField(upload_to='characters/art/', blank=True, null=True, verbose_name="Референсы/Арты")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Анкету"
        verbose_name_plural = "Анкеты"
    
    def __str__(self):
        return f"{self.name} — {self.get_status_display()}"
    
    def get_status_display(self):
        statuses = {
            'pending': '⛧ На проверке',
            'approved': '⚜ Одобрено',
            'declined': '☠ Отказано',
            'edited': '📝 Требует изменений',
        }
        return statuses.get(self.status, '❓ Неизвестно')
    
    def get_absolute_url(self):
        return reverse('character_detail', args=[self.id])

class Comment(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=2000, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
    
    def __str__(self):
        return f"{self.author.username} → {self.character.name}"

class UserProfile(models.Model):
    REPUTATION_CHOICES = [
        ('good', '⚜ Хороший постоялец'),
        ('warning', '⚠️ Оставляет желать лучшего'),
        ('aggressive', '💀 Агрессивный постоялец'),
        ('new', '✨ Новый постоялец'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")
    bio = models.TextField(blank=True, max_length=1000, verbose_name="О себе")
    discord = models.CharField(max_length=100, blank=True, verbose_name="Discord")
    telegram = models.CharField(max_length=100, blank=True, verbose_name="Telegram")
    website = models.URLField(blank=True, verbose_name="Сайт/Портфолио")
    location = models.CharField(max_length=200, blank=True, verbose_name="Местоположение")
    reputation = models.CharField(max_length=20, choices=REPUTATION_CHOICES, default='new', verbose_name="Репутация")
    admin_note = models.TextField(blank=True, verbose_name="Заметка администратора (только для админов)")
    registration_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username
    
    def get_character_count(self):
        return self.user.characters.count()
    
    def get_absolute_url(self):
        return reverse('profile', args=[self.user.username])
    
    def get_reputation_badge(self):
        badges = {
            'good': '<span class="reputation-good">⚜ Хороший постоялец</span>',
            'warning': '<span class="reputation-warning">⚠️ Оставляет желать лучшего</span>',
            'aggressive': '<span class="reputation-aggressive">💀 Агрессивный постоялец</span>',
            'new': '<span class="reputation-new">✨ Новый постоялец</span>',
        }
        return badges.get(self.reputation, badges['new'])

# Сигналы для автоматического создания профиля
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Проверяем, существует ли профиль, прежде чем сохранять
    if hasattr(instance, 'profile'):
        instance.profile.save()