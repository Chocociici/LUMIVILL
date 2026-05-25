from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, DetailView
from .models import News, Event, Character, CharacterImage, Comment, UserProfile
from .forms import CharacterForm, UserProfileForm

# ===== НОВОСТИ =====
class NewsListView(ListView):
    model = News
    template_name = 'news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10
    
    def get_queryset(self):
        return News.objects.filter(is_published=True)

class NewsDetailView(DetailView):
    model = News
    template_name = 'news_detail.html'
    context_object_name = 'news_item'

# ===== ИВЕНТЫ =====
class EventListView(ListView):
    model = Event
    template_name = 'events_list.html'
    context_object_name = 'events_list'
    paginate_by = 10
    
    def get_queryset(self):
        return Event.objects.filter(is_published=True)

class EventDetailView(DetailView):
    model = Event
    template_name = 'event_detail.html'
    context_object_name = 'event_item'

# ===== ГЛАВНАЯ =====
def home(request):
    recent_news = News.objects.filter(is_published=True)[:5]
    recent_events = Event.objects.filter(is_published=True)[:3]
    return render(request, 'home.html', {
        'recent_news': recent_news,
        'recent_events': recent_events,
    })

# ===== АНКЕТЫ =====
def catalog(request):
    characters = Character.objects.all().order_by('-created_at')
    
    search_query = request.GET.get('search', '')
    if search_query:
        characters = characters.filter(
            Q(name__icontains=search_query) |
            Q(race__icontains=search_query) |
            Q(age__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    race_filter = request.GET.get('race', '')
    if race_filter:
        characters = characters.filter(race=race_filter)
    
    gender_filter = request.GET.get('gender', '')
    if gender_filter:
        characters = characters.filter(gender=gender_filter)
    
    paginator = Paginator(characters, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    races = Character.objects.values_list('race', flat=True).distinct()
    
    return render(request, 'catalog.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'race_filter': race_filter,
        'gender_filter': gender_filter,
        'races': races,
    })

def character_detail(request, pk):
    character = get_object_or_404(Character, pk=pk)
    comments = character.comments.all()
    return render(request, 'character_detail.html', {
        'character': character,
        'comments': comments,
    })

@login_required
def create_character(request):
    if request.method == 'POST':
        form = CharacterForm(request.POST, request.FILES)
        if form.is_valid():
            character = form.save(commit=False)
            character.author = request.user
            character.save()
            
            extra_images = request.FILES.getlist('extra_images')
            for img in extra_images:
                CharacterImage.objects.create(character=character, image=img)
            
            return redirect('character_detail', pk=character.id)
    else:
        form = CharacterForm()
    return render(request, 'create_character.html', {'form': form})

@login_required
def edit_character(request, pk):
    character = get_object_or_404(Character, pk=pk, author=request.user)
    if request.method == 'POST':
        form = CharacterForm(request.POST, request.FILES, instance=character)
        if form.is_valid():
            character = form.save()
            character.status = 'pending'
            character.save()
            
            extra_images = request.FILES.getlist('extra_images')
            for img in extra_images:
                CharacterImage.objects.create(character=character, image=img)
            
            return redirect('character_detail', pk=character.id)
    else:
        form = CharacterForm(instance=character)
    return render(request, 'edit_character.html', {'form': form, 'character': character})

@login_required
def delete_character(request, pk):
    character = get_object_or_404(Character, pk=pk)
    if request.user == character.author or request.user.is_staff:
        character.delete()
        return redirect('catalog')
    return redirect('character_detail', pk=pk)

@login_required
def add_comment(request, character_id):
    character = get_object_or_404(Character, pk=character_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Comment.objects.create(
                character=character,
                author=request.user,
                text=text
            )
    return redirect('character_detail', pk=character_id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author == request.user or request.user.is_staff:
        character_id = comment.character.id
        comment.delete()
    return redirect('character_detail', pk=character_id)

# ===== ПРОФИЛИ =====
def profile_view(request, username):
    profile = get_object_or_404(UserProfile, user__username=username)
    characters = Character.objects.filter(author=profile.user)
    return render(request, 'profile.html', {
        'profile': profile,
        'characters': characters,
    })

@login_required
def edit_profile(request):
    profile = request.user.profile  # ← здесь ошибка, если у пользователя нет профиля
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

@staff_member_required
def admin_character_list(request):
    characters = Character.objects.all().order_by('-created_at')
    pending_count = characters.filter(status='pending').count()
    return render(request, 'admin_character_list.html', {
        'characters': characters,
        'pending_count': pending_count,
    })