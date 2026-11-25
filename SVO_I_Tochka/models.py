from django.db import models
from django.contrib.auth.models import User


class SpectralClass(models.Model):
    name = models.CharField('Название класса', max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Спектральный класс'
        verbose_name_plural = 'Спектральные классы'


class Composition(models.Model):
    name = models.CharField('Элемент состава', max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Элемент состава'
        verbose_name_plural = 'Элементы состава'


class Asteroid(models.Model):
    STATUS_CHOICES = [
        ('in_sale', 'В продаже'),
        ('sold', 'Продан'),
        ('reserved', 'Резерв'),
    ]

    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    price = models.PositiveIntegerField('Цена (в крышках)')
    distance = models.PositiveIntegerField('Расстояние (км)')
    image = models.ImageField('Фотография', upload_to='asteroids/', blank=True, null=True)
    spectral_class = models.ForeignKey(
        SpectralClass,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Спектральный класс'
    )
    compositions = models.ManyToManyField(
        Composition,
        blank=True,
        verbose_name='Состав и теги'
    )
    is_sold = models.BooleanField('Продан', default=False)
    status = models.CharField(
        'Статус лота',
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_sale',
    )
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    @property
    def price_display(self):
        return f"{self.price:,}".replace(",", ".")

    def __str__(self):
        return f"{self.title} ({self.price_display} крышек)"

    class Meta:
        verbose_name = 'Астероид'
        verbose_name_plural = 'Астероиды'


class Order(models.Model):
    STATUS_CHOICES = [
        ('in_transit', 'В доставке'),
        ('completed', 'Завершён'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Покупатель')
    asteroid = models.ForeignKey(Asteroid, on_delete=models.CASCADE, verbose_name='Астероид')
    code = models.CharField('Номер заказа', max_length=20, blank=True)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_transit',
    )
    created_at = models.DateTimeField('Дата покупки', auto_now_add=True)

    @property
    def display_code(self):
        return self.code or f"#SO-{self.pk:04d}"

    def __str__(self):
        return f"{self.display_code} — {self.asteroid.title} ({self.user.email})"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь',
    )
    balance = models.PositiveIntegerField('Баланс (в крышках)', default=8_400_000)

    @property
    def balance_display(self):
        return f"{self.balance:,}".replace(",", ".")

    @property
    def colonist_number(self):
        return f"{self.user_id + 321:05d}"

    def __str__(self):
        return f"Профиль {self.user.username}"

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
