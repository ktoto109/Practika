from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Asteroid, SpectralClass, Composition, Order, Profile


def index(request):
    asteroids = Asteroid.objects.filter(is_sold=False).order_by('-created_at')[:6]
    return render(request, 'index.html', {'asteroids': asteroids})


def _to_ints(values):
    result = []
    for value in values:
        try:
            result.append(int(value))
        except (TypeError, ValueError):
            continue
    return result


def catalog(request):
    asteroids = Asteroid.objects.filter(is_sold=False)
    spectral_classes = SpectralClass.objects.all()
    compositions = Composition.objects.all()

    selected_compositions = _to_ints(request.GET.getlist('composition'))
    selected_classes = _to_ints(request.GET.getlist('spectral_class'))
    dist_from_raw = request.GET.get('dist_from', '')
    dist_to_raw = request.GET.get('dist_to', '')
    sort_by = request.GET.get('sort', 'price_asc')
    if sort_by not in ('price_asc', 'price_desc'):
        sort_by = 'price_asc'

    if selected_compositions:
        asteroids = asteroids.filter(compositions__id__in=selected_compositions).distinct()
    if selected_classes:
        asteroids = asteroids.filter(spectral_class__id__in=selected_classes)

    try:
        if dist_from_raw:
            asteroids = asteroids.filter(distance__gte=int(dist_from_raw))
        if dist_to_raw:
            asteroids = asteroids.filter(distance__lte=int(dist_to_raw))
    except ValueError:
        pass

    if sort_by == 'price_desc':
        asteroids = asteroids.order_by('-price')
    else:
        asteroids = asteroids.order_by('price')

    context = {
        'asteroids': asteroids,
        'spectral_classes': spectral_classes,
        'compositions': compositions,
        'selected_compositions': selected_compositions,
        'selected_classes': selected_classes,
        'dist_from': dist_from_raw,
        'dist_to': dist_to_raw,
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
        login_value = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=login_value, password=password)
        if user is None and login_value:
            user_by_email = User.objects.filter(email__iexact=login_value).first()
            if user_by_email is not None:
                user = authenticate(request, username=user_by_email.username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        error = 'Неверный логин, email или пароль'
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
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('index')
    return render(request, 'register.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required(login_url='login')
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()

        error = None
        if not name:
            error = 'Укажите имя'
        elif not email:
            error = 'Укажите email'
        else:
            try:
                validate_email(email)
            except ValidationError:
                error = 'Некорректный email'
            else:
                email_taken = User.objects.filter(email__iexact=email).exclude(pk=request.user.pk).exists()
                if email_taken:
                    error = 'Этот email уже используется'

        if error:
            messages.error(request, error)
        else:
            request.user.first_name = name
            request.user.email = email
            request.user.save(update_fields=['first_name', 'email'])
            messages.success(request, 'Изменения сохранены')
            return redirect('profile')

    orders = Order.objects.filter(user=request.user).select_related('asteroid').order_by('-created_at')
    return render(
        request,
        'profile.html',
        {
            'profile': profile_obj,
            'orders': orders,
        },
    )
