"""
URL configuration for SRTimeWeb project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# from core.views import api_v1_info # Commenting out to avoid import error if not exists

urlpatterns = [
    # Admin and API
    path('admin/', admin.site.urls),
    # path('api/v1/', api_v1_info, name='api_v1_info'),
    path('api/v1/', include('core.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    from django.views.static import serve
    static_root = str(settings.BASE_DIR / 'static')
    
    # Rutas explícitas para archivos estáticos del frontend
    urlpatterns += [
        re_path(r'^assets/(?P<path>.*)$', serve, {'document_root': static_root + '/assets'}),
        re_path(r'^img/(?P<path>.*)$', serve, {'document_root': static_root + '/img'}),
        re_path(r'^vite\.svg$', serve, {'document_root': static_root, 'path': 'vite.svg'}),
    ]

# SPA routes (index.html para todas las rutas no manejadas)
urlpatterns += [
    path('', TemplateView.as_view(template_name='index.html'), name='spa_index'),
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html'), name='spa_catch_all'),
]
