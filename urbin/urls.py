from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import detection.urls

urlpatterns = [
    path('', include('detection.urls')),  # Le routage principal vers ton app
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
