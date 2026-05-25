from django import forms
from .models import Character, CharacterImage, UserProfile

class CharacterForm(forms.ModelForm):
    extra_images = forms.ImageField(
        label="Дополнительные изображения",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Character
        exclude = ['author', 'status', 'admin_comment', 'created_at', 'updated_at', 'gallery']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя и фамилия, псевдоним'}),
            'age': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '28 лет / 800 лет'}),
            'gender': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Женский / Мужской'}),
            'height_weight': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '183 см, 51 кг'}),
            'race': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Кицунэ, Человек, Вампир...'}),
            'faction': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фракция (если есть)'}),
            'appearance': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'personality': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'combat_skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'racial_abilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'magic': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'inventory': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'documents': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'weaknesses': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'main_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'music': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'pony_town_skin': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'voice_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'art_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'discord', 'telegram', 'website', 'location']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Расскажите о себе...'}),
            'discord': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Discord username'}),
            'telegram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Город, страна'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }