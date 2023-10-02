from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home_menu.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
