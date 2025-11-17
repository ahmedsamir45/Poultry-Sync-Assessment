from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'orders', views.OrderViewSet, basename='order')

app_name = 'api'

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Authentication
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    
    # Custom endpoints
    path('orders/export/', views.OrderViewSet.as_view({'get': 'export'}), name='order-export'),
    path('products/bulk-delete/', views.ProductViewSet.as_view({'delete': 'bulk_delete'}), name='product-bulk-delete'),
    path('products/<uuid:pk>/delete/', views.ProductViewSet.as_view({'delete': 'destroy'}), name='product-delete'),
    path('products/create/', views.create_product, name='product-create'),
    path('products/<uuid:pk>/toggle-active/', views.toggle_product_active, name='product-toggle-active'),
    path('orders/create/', views.create_order, name='order-create'),
    
    # Login/Logout views
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Index view
    path('', views.index, name='index'),
]