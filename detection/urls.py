from django.urls import path
from . import views
from django.shortcuts import render
from .views import hello_world, register_user, login_user, UpdateUserView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('upload/', views.upload_image, name='upload_image'),
    path('success/', lambda r: render(r, 'success.html'), name='image_success'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/hello/', hello_world),
    path('api/register/', register_user),
    path('api/login/', login_user),
    path("api/bins/", views.bins_data, name="bins_data"),
    path('api/update-user/', UpdateUserView.as_view()),
    path('api/user/me/', views.get_user_profile),
    path('api/user/update/', views.update_user_profile),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/upload-image/', views.upload_image_api, name='upload_image_api'),
]