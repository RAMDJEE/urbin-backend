from django.urls import path
from detection import views

urlpatterns = [
    path('api/login/', views.login_user),
    path('api/register/', views.register_user),
    path('api/bins/', views.bins_data),     # <--- Remis ici
    path('', views.upload_image, name='upload_image'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]