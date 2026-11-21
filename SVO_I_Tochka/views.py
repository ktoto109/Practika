from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Asteroid, SpectralClass, Composition, Order


def index(request):
    asteroids = Asteroid.objects.filter(is_sold=False).order_by('-created_at')[:6]
    return render(request, 'index.html', {'asteroids': asteroids})


def catalog(request):
    asteroids = Asteroid.objects.filter(is_sold=False)
    spectral_classes = SpectralClass.objects.all()
    compositions = Composition.objects.all()

    selected_compositions = request.GET.getlist('composition')
    selected_classes = request.GET.getlist('spectral_class')
    dist_from = request.GET.get('dist_from')
    dist_to = request.GET.get('dist_to')
    sort_by = request.GET.get('sort', 'price_asc')

    if selected_compositions:
        asteroids = asteroids.filter(compositions__id__in=selected_compositions).distinct()
    if selected_classes:
        asteroids = asteroids.filter(spectral_class__id__in=selected_classes)
    if dist_from:
        asteroids = asteroids.filter(distance__gte=dist_from)
    if dist_to:
        asteroids = asteroids.filter(distance__lte=dist_to)

    if sort_by == 'price_desc':
        asteroids = asteroids.order_by('-price')
    else:
        asteroids = asteroids.order_by('price')

    context = {
        'asteroids': asteroids,
        'spectral_classes': spectral_classes,
        'compositions': compositions,
        'selected_compositions': [int(i) for i in selected_compositions],
        'selected_classes': [int(i) for i in selected_classes],
        'dist_from': dist_from or '',
        'dist_to': dist_to or '',
        'sort_by': sort_by,
    }
    return render(request, 'catalog.html', context)


def asteroid_detail(request, pk):
    asteroid = get_object_or_404(Asteroid, pk=pk)
    return render(request, 'detail.html', {'asteroid': asteroid})


@login_required(login_url='login')
def buy_asteroid(request, pk):
    if request.method == 'POST':
        asteroid = get_object_or_404(Asteroid, pk=pk, is_sold=False)
        Order.objects.create(user=request.user, asteroid=asteroid)
        asteroid.is_sold = True
        asteroid.save()
        return redirect('catalog')
    return redirect('asteroid_detail', pk=pk)


def login_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('index')
        error = 'Неверный email или пароль'
    return render(request, 'login.html', {'error': error})


def register_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            error = 'Пароли не совпадают'
        elif User.objects.filter(username=email).exists():
            error = 'Пользователь с таким email уже зарегистрирован'
        else:
            user = User.objects.create_user(username=email, email=email, password=password)
            login(request, user)
            return redirect('index')
    return render(request, 'register.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required(login_url='login')
def profile(request):
    return render(request, 'profile.html')
