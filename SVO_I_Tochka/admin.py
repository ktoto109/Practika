from django.contrib import admin

from .models import Asteroid, Composition, Order, Profile, SpectralClass


@admin.register(SpectralClass)
class SpectralClassAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Composition)
class CompositionAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Asteroid)
class AsteroidAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'distance', 'spectral_class', 'is_sold')
    list_filter = ('spectral_class', 'is_sold')
    search_fields = ('title', 'description')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('display_code', 'user', 'asteroid', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('code', 'user__username', 'asteroid__title')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')
    search_fields = ('user__username', 'user__email')
