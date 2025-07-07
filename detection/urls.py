from django.urls import path
from django.urls import path
from . import views
from .views import hello_world, register_user, login_user

urlpatterns = [
    path('api/login/', views.login_user),
    path('api/register/', views.register_user),
    path('', views.upload_image, name='upload_image'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]