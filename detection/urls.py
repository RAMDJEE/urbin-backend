from django.urls import path
from . import views
from .views import hello_world, register_user, login_user

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
]