"""
URL configuration for emiage_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', core_views.sitemap_xml, name='sitemap_xml'),
    path('robots.txt', core_views.robots_txt, name='robots_txt'),
    path('sw.js', core_views.service_worker, name='service_worker'),
    path('', include('core.urls')),  # Inclure les URLs de l'application core
]

# Ajout des URLs pour servir les fichiers média et statiques en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# En production (Render, DEBUG=False), les statiques sont servies par WhiteNoise.
# Les fichiers média (documents pédagogiques) sont servis par Django lui-même :
# acceptable à cette échelle (site de ~130 Mo), permet de rester sur le plan gratuit
# sans service de stockage externe.
if not settings.DEBUG:
    from django.views.static import serve as media_serve

    urlpatterns += [
        path(
            f'{settings.MEDIA_URL.lstrip("/")}<path:path>',
            media_serve,
            {'document_root': settings.MEDIA_ROOT},
        ),
    ]
