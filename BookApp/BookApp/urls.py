"""
URL configuration for BookApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, re_path
from BookDBMS import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.index, name='index'),
    re_path(r'^.*login\.html$', views.login_view, name='login_view'),
    re_path(r'^.*inventory\.html$', views.inventory, name='inventory'),
    path('edit_book/<int:pk>/', views.edit_book, name='edit_book'),
    re_path(r'^.*stock\.html$', views.stock, name='stock'),
    re_path(r'^.*stock_partial\.html$', views.stock_partial, name='stock_partial'),
    re_path(r'^.*stock_complete\.html$', views.stock_complete, name='stock_complete'),
    re_path(r'^.*check_unpaid\.html$', views.check_unpaid, name='check_unpaid'),
    path('payment/<int:pk>/', views.payment, name='payment'),
    re_path(r'^.*payment\.html/<int:pk>/$', views.payment, name='payment'),
    re_path(r'^.*check_unreturned\.html$', views.check_unreturned, name='check_unreturned'),
    path('return_book/<int:pk>/', views.return_book, name='return_book'),
    re_path(r'^.*purchase\.html$', views.purchase, name='purchase'),
    re_path(r'^.*purchase_success\.html$', views.purchase_success, name='purchase_success'),
    re_path(r'^.*purchase_fail\.html$', views.purchase_fail, name='purchase_fail'),
    re_path(r'^.*personal_profile\.html$', views.profile_view, name='profile_view'),
    re_path(r'^.*edit_profile\.html$', views.edit_profile, name='edit_profile'),
]
