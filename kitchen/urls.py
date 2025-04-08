"""
URL configuration for hello_world project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect # Import redirect

from kitchen.core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include inventory URLs under the 'inventory/' path
    path('inventory/', include('inventory.urls', namespace='inventory')),
    # Add django_browser_reload URLs
    path("__reload__/", include("django_browser_reload.urls")),
    # Redirect the root URL to the inventory list
    path('', lambda request: redirect('inventory:inventory_list', permanent=True)),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
