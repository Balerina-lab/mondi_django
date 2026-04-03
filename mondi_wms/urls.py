from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Ovde je bila greška: mora biti .urls a ne .status
    path('admin/', admin.site.urls), 
    path('', include('core.urls')),
]

# Dodatak za prikazivanje slika tokom razvoja
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)