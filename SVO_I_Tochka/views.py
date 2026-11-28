from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db.models import Count, Q, Sum
from .forms import AsteroidForm
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
        asteroid.status = 'sold'
        asteroid.save(update_fields=['is_sold', 'status'])
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


@staff_member_required(login_url='login')
def admin_panel(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', 'all')

    asteroids = Asteroid.objects.all().order_by('-id')
    if query:
        if query.isdigit():
            asteroids = asteroids.filter(Q(title__icontains=query) | Q(pk=int(query)))
        else:
            asteroids = asteroids.filter(title__icontains=query)

    if status in dict(Asteroid.STATUS_CHOICES):
        asteroids = asteroids.filter(status=status)

    found_count = asteroids.count()
    paginator = Paginator(asteroids, 4)
    page_obj = paginator.get_page(request.GET.get('page'))

    revenue = Order.objects.aggregate(total=Sum('asteroid__price'))['total'] or 0

    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'q': query,
        'status': status,
        'found_count': found_count,
        'total_lots': Asteroid.objects.count(),
        'active_orders': Order.objects.filter(status='in_transit').count(),
        'users_count': User.objects.count(),
        'revenue_display': f"{revenue:,}".replace(',', '.'),
        'status_choices': Asteroid.STATUS_CHOICES,
    }
    return render(request, 'admin_panel.html', context)


@staff_member_required(login_url='login')
def admin_lot_add(request):
    form = AsteroidForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        asteroid = form.save(commit=False)
        asteroid.is_sold = asteroid.status == 'sold'
        asteroid.save()
        form.save_m2m()
        messages.success(request, f'Лот «{asteroid.title}» добавлен.')
        return redirect('admin_panel')

    return render(
        request,
        'admin_lot_form.html',
        {
            'form': form,
            'is_edit': False,
        },
    )


@staff_member_required(login_url='login')
def admin_lot_edit(request, pk):
    asteroid = get_object_or_404(Asteroid, pk=pk)
    old_image = asteroid.image if asteroid.image else None
    old_image_name = old_image.name if old_image else None
    form = AsteroidForm(request.POST or None, request.FILES or None, instance=asteroid)

    if request.method == 'POST' and form.is_valid():
        asteroid = form.save(commit=False)
        asteroid.is_sold = asteroid.status == 'sold'
        asteroid.save()
        form.save_m2m()

        new_image_name = asteroid.image.name if asteroid.image else None
        if old_image and old_image_name != new_image_name:
            old_image.delete(save=False)

        messages.success(request, f'Лот «{asteroid.title}» сохранён.')
        return redirect('admin_panel')

    return render(
        request,
        'admin_lot_form.html',
        {
            'form': form,
            'asteroid': asteroid,
            'is_edit': True,
        },
    )


@staff_member_required(login_url='login')
def admin_lot_delete(request, pk):
    asteroid = get_object_or_404(Asteroid, pk=pk)

    if request.method == 'POST':
        title = asteroid.title
        image = asteroid.image if asteroid.image else None
        asteroid.delete()
        if image:
            image.delete(save=False)
        messages.success(request, f'Лот «{title}» удалён.')
        return redirect('admin_panel')

    return render(request, 'admin_lot_delete.html', {'asteroid': asteroid})


@staff_member_required(login_url='login')
def admin_orders(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', 'all')

    orders = Order.objects.select_related('user', 'asteroid').order_by('-created_at')
    if query:
        orders = orders.filter(
            Q(code__icontains=query)
            | Q(user__username__icontains=query)
            | Q(user__email__icontains=query)
            | Q(asteroid__title__icontains=query)
        )

    if status in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status)

    found_count = orders.count()
    paginator = Paginator(orders, 6)
    page_obj = paginator.get_page(request.GET.get('page'))

    revenue = Order.objects.aggregate(total=Sum('asteroid__price'))['total'] or 0

    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'q': query,
        'status': status,
        'found_count': found_count,
        'total_orders': Order.objects.count(),
        'in_transit_count': Order.objects.filter(status='in_transit').count(),
        'completed_count': Order.objects.filter(status='completed').count(),
        'revenue_display': f"{revenue:,}".replace(',', '.'),
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'admin_orders.html', context)


@staff_member_required(login_url='login')
def admin_order_toggle(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        order.status = 'completed' if order.status == 'in_transit' else 'in_transit'
        order.save(update_fields=['status'])
        messages.success(request, f'Статус заказа {order.display_code} изменён.')

    return redirect('admin_orders')


@staff_member_required(login_url='login')
def admin_users(request):
    query = request.GET.get('q', '').strip()
    role = request.GET.get('role', 'all')

    for user in User.objects.all():
        Profile.objects.get_or_create(user=user)

    users = User.objects.select_related('profile').annotate(orders_count=Count('order')).order_by('id')
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
        )

    if role == 'staff':
        users = users.filter(is_staff=True)
    elif role == 'colonists':
        users = users.filter(is_staff=False)

    found_count = users.count()
    paginator = Paginator(users, 8)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'q': query,
        'role': role,
        'found_count': found_count,
        'total_users': User.objects.count(),
        'staff_count': User.objects.filter(is_staff=True).count(),
        'colonist_count': User.objects.filter(is_staff=False).count(),
        'total_orders': Order.objects.count(),
    }
    return render(request, 'admin_users.html', context)
