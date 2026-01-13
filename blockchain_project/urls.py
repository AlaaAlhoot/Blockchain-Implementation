# blockchain_project/urls.py
"""
URL configuration for blockchain_project project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Redirect root to blockchain app
    path('', RedirectView.as_view(url='/blockchain/', permanent=False)),
    
    # Blockchain app URLs
    path('blockchain/', include('blockchain.urls', namespace='blockchain')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize admin site
admin.site.site_header = "Blockchain Administration"
admin.site.site_title = "Blockchain Admin Portal"
admin.site.index_title = "Welcome to Blockchain Administration"