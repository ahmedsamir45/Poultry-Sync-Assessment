"""
URL configuration for Poultry_Sync_Assessment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from api.views import index

# API URL Patterns
urlpatterns = [
    # Root URL points to the index view
    path('', index, name='index'),
    
    # Admin site
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('api.urls')),
    
    # REST framework auth URLs with namespace
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # Authentication URLs - using csrf_exempt for the login view
    # path('accounts/login/', csrf_exempt(auth_views.LoginView.as_view(template_name='rest_framework/login.html')), name='login'),
    # path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    # Admin login (separate from main login)
    # path('admin/login/', csrf_exempt(auth_views.LoginView.as_view(template_name='admin/login.html')), name='admin_login'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # ReDoc
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
