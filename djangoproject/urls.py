"""
URL configuration for djangoproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from SVO_I_Tochka import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('asteroid/<int:pk>/', views.asteroid_detail, name='asteroid_detail'),
    path('asteroid/<int:pk>/buy/', views.buy_asteroid, name='buy_asteroid'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/lots/add/', views.admin_lot_add, name='admin_lot_add'),
    path('admin-panel/lots/<int:pk>/edit/', views.admin_lot_edit, name='admin_lot_edit'),
    path('admin-panel/lots/<int:pk>/delete/', views.admin_lot_delete, name='admin_lot_delete'),
    path('admin-panel/orders/', views.admin_orders, name='admin_orders'),
    path('admin-panel/orders/<int:pk>/toggle/', views.admin_order_toggle, name='admin_order_toggle'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


