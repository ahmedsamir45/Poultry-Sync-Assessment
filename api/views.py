from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action, permission_classes, authentication_classes, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
import csv
import json
from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate
from django.db import transaction
from .models import Product, Order, Company, CustomUser
from .serializers import ProductSerializer, OrderSerializer, UserSerializer
from rest_framework.authtoken.models import Token
from pathlib import Path

def _log_order_confirmation(order):
    """Log order confirmation to file (simulating email)"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / 'order_confirmations.log'
    
    customer_email = order.created_by.email if order.created_by and order.created_by.email else 'N/A'
    
    log_message = (
        f"[{timezone.now().isoformat()}] ORDER CONFIRMATION EMAIL\n"
        f"To: {customer_email}\n"
        f"Subject: Order Confirmation - Order #{order.id}\n"
        f"\n"
        f"Dear {order.created_by.get_full_name() or order.created_by.username},\n"
        f"\n"
        f"Your order has been confirmed!\n"
        f"\n"
        f"Order Details:\n"
        f"  Order ID: {order.id}\n"
        f"  Product: {order.product.name}\n"
        f"  Quantity: {order.quantity}\n"
        f"  Status: {order.get_status_display()}\n"
        f"  Order Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"  Shipped At: {order.shipped_at.strftime('%Y-%m-%d %H:%M:%S') if order.shipped_at else 'N/A'}\n"
        f"\n"
        f"Thank you for your order!\n"
        f"{'=' * 80}\n"
    )
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_message)

class IsCompanyMember(permissions.BasePermission):
    """Permission to ensure user belongs to a company and can access company data"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.company is not None

    def has_object_permission(self, request, view, obj):
        # Users can only access their own company's data
        if hasattr(obj, 'company'):
            return obj.company == request.user.company
        if hasattr(obj, 'get_company'):
            return obj.get_company() == request.user.company
        return False

from functools import wraps
from django.views.decorators.http import require_http_methods

def csrf_exempt_login_required(view_func):
    """
    A decorator that applies csrf_exempt and login_required to a view function.
    """
    @wraps(view_func)
    @csrf_exempt
    @login_required
    def wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapped_view

class LoginView(APIView):
    """
    View to handle user login and return authentication token.
    """
    authentication_classes = []
    permission_classes = []
    template_name = 'rest_framework/login.html'
    
    def get(self, request, *args, **kwargs):
        # If user is already authenticated, redirect to home
        if request.user.is_authenticated:
            return redirect('/')
        return Response({}, template_name=self.template_name)
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        next_url = request.data.get('next', '/')
        
        try:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    # For API requests, return token; for web, redirect
                    if request.accepted_renderer.format == 'api':
                        token, created = Token.objects.get_or_create(user=user)
                        return Response({
                            'token': token.key,
                            'user_id': user.pk,
                            'username': user.username,
                            'is_admin': user.is_staff
                        })
                    return redirect(next_url)
                else:
                    error_msg = 'This account is inactive.'
            else:
                error_msg = 'Invalid username or password.'
                
        except Exception as e:
            error_msg = 'An error occurred during login. Please try again.'
            
        # For API requests, return error as JSON
        if request.accepted_renderer and request.accepted_renderer.format == 'api':
            return Response(
                {'error': error_msg},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # For web requests, show error message and render login page
        messages.error(request, error_msg)
        return Response(
            {'error': error_msg}, 
            template_name=self.template_name,
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """
    View to handle user logout.
    """
    def post(self, request):
        try:
            # Delete the user's token if it exists
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()
                
            # Logout the user
            if request.user.is_authenticated:
                auth_logout(request)
                
            # For API requests, return success message
            if request.accepted_renderer and request.accepted_renderer.format == 'api':
                return Response(
                    {'message': 'Successfully logged out.'},
                    status=status.HTTP_200_OK
                )
                
            # For web requests, redirect to login page with success message
            messages.success(request, 'You have been successfully logged out.')
            return redirect('login')
            
        except Exception as e:
            error_msg = 'An error occurred during logout.'
            if request.accepted_renderer and request.accepted_renderer.format == 'api':
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            messages.error(request, error_msg)
            return redirect('login')


@csrf_exempt_login_required
@require_http_methods(["GET", "POST"])
def index(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        is_active = request.POST.get('is_active', 'true').lower() == 'true'
        
        if name and price and stock:
            # Create a new product
            Product.objects.create(
                name=name,
                price=price,
                stock=stock,
                is_active=is_active,
                company=request.user.company,
                created_by=request.user
            )
    
    # Get all products for the user's company (not just active ones)
    products = Product.objects.filter(
        company=request.user.company
    ).order_by('-created_at')
    
    # Get orders for the user's company
    orders = Order.objects.filter(
        company=request.user.company
    ).select_related('product', 'created_by').order_by('-created_at')
    
    # Add can_edit flag to each order
    today = timezone.now().date()
    for order in orders:
        order.can_edit = order.can_user_edit(request.user)
    
    return render(request, 'index.html', {
        'products': products,
        'orders': orders,
        'user': request.user
    })

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsCompanyMember]
    
    def get_queryset(self):
        # For list action, return only active products (per requirements)
        # For other actions (update, retrieve, destroy), return all products
        # This allows editing and deleting inactive products
        if self.action in ['list']:
            return Product.objects.filter(company=self.request.user.company, is_active=True)
        else:
            # Include all products (active and inactive) for update, retrieve, and destroy
            return Product.objects.filter(company=self.request.user.company)
    
    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company, created_by=self.request.user)
    
    def perform_destroy(self, instance):
        # Both admins and operators can delete products
        if not (self.request.user.is_admin or self.request.user.is_operator):
            raise permissions.PermissionDenied("Only admins and operators can delete products")
        instance.soft_delete()
        
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """Bulk soft-delete products"""
        if not (request.user.is_admin or request.user.is_operator):
            return Response(
                {"detail": "Only admins and operators can delete products"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        product_ids = request.query_params.getlist('ids') or request.data.get('ids', [])
        
        if not product_ids:
            return Response(
                {"detail": "No product IDs provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        products = Product.objects.filter(
            id__in=product_ids,
            company=request.user.company
        )
        count = products.count()
        for product in products:
            product.soft_delete()
        
        return Response(
            {"detail": f"Soft-deleted {count} product(s)"}, 
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, *args, **kwargs):
        # Single delete - can delete both active and inactive products
        from django.http import Http404
        
        # Check permissions first
        if not (request.user.is_admin or request.user.is_operator):
            return Response(
                {"detail": "Only admins and operators can delete products"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            instance = self.get_object()
        except Http404:
            return Response(
                {"detail": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Soft delete the product (set is_active=False)
        # This works for both active and inactive products
        was_active = instance.is_active
        instance.soft_delete()
        
        # Return a message indicating the result
        if was_active:
            message = "Product deleted successfully (marked as inactive)"
        else:
            message = "Product is already inactive"
        
        return Response(
            {"detail": message, "is_active": False}, 
            status=status.HTTP_200_OK
        )

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsCompanyMember]
    
    def get_queryset(self):
        return Order.objects.filter(company=self.request.user.company)
    
    def create(self, request, *args, **kwargs):
        # Only admins can create orders
        if not request.user.is_admin:
            return Response(
                {"detail": "Only admins can create orders"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Support both single and multiple orders
        data = request.data
        is_list = isinstance(data, list)
        orders_data = data if is_list else [data]
        
        created_orders = []
        errors = []
        
        with transaction.atomic():
            for idx, order_data in enumerate(orders_data):
                serializer = self.get_serializer(data=order_data)
                
                if not serializer.is_valid():
                    errors.append({
                        'index': idx,
                        'errors': serializer.errors
                    })
                    continue
                
                try:
                    # Validate product is active
                    product = serializer.validated_data['product']
                    quantity = serializer.validated_data['quantity']
                    
                    if not product.is_active:
                        errors.append({
                            'index': idx,
                            'errors': {'product': ['Product is not active']}
                        })
                        continue
                    
                    # Check stock (but don't deduct yet - order is pending)
                    if product.stock < quantity:
                        errors.append({
                            'index': idx,
                            'errors': {'quantity': ['Insufficient stock']}
                        })
                        continue
                    
                    # Create order with PENDING status
                    order = serializer.save(
                        company=request.user.company,
                        created_by=request.user,
                        status=Order.Status.PENDING
                    )
                    
                    # Don't update stock or log email yet - order is pending
                    # Stock will be deducted and email logged when status changes to SUCCESS
                    
                    created_orders.append(order)
                    
                except Exception as e:
                    errors.append({
                        'index': idx,
                        'errors': {'detail': [str(e)]}
                    })
        
        if errors and not created_orders:
            return Response(
                {"detail": "Failed to create orders", "errors": errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if is_list:
            serializer = self.get_serializer(created_orders, many=True)
            response_data = serializer.data
            if errors:
                response_data = {
                    'created': response_data,
                    'errors': errors
                }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            if created_orders:
                serializer = self.get_serializer(created_orders[0])
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"detail": "Failed to create order", "errors": errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
    
    def _log_order_confirmation(self, order):
        """Log order confirmation to file (simulating email)"""
        _log_order_confirmation(order)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        if request.user.is_viewer:
            return Response(
                {"detail": "Insufficient permissions"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        orders = Order.objects.filter(company=request.user.company)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Product', 'Quantity', 'Status', 'Created At', 'Shipped At', 'Created By'])
        
        for order in orders:
            writer.writerow([
                order.id,
                order.product.name,
                order.quantity,
                order.get_status_display(),
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                order.shipped_at.strftime('%Y-%m-%d %H:%M:%S') if order.shipped_at else 'N/A',
                order.created_by.username if order.created_by else 'N/A'
            ])
        
        return response
        
    def update(self, request, *args, **kwargs):
        # Only allow admins or operators (operators can edit orders created today)
        order = self.get_object()
        old_status = order.status
        
        if not order.can_user_edit(request.user):
            if request.user.is_operator:
                return Response(
                    {"detail": "You can only edit orders created today"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            return Response(
                {"detail": "You don't have permission to edit this order"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update the order
        response = super().update(request, *args, **kwargs)
        
        # If status changed to SUCCESS, log the confirmation email
        if response.status_code == 200:  # Update was successful
            order.refresh_from_db()
            if order.status == Order.Status.SUCCESS and old_status != Order.Status.SUCCESS:
                _log_order_confirmation(order)
            
        return response


@api_view(['POST'])
@permission_classes([IsCompanyMember])
def create_product(request):
    """
    Create a new product
    """
    try:
        data = request.data if hasattr(request, 'data') else request.POST
        
        # Get the product data
        name = data.get('name')
        price = data.get('price')
        stock = data.get('stock')
        is_active = data.get('is_active', True)
        
        if not all([name, price, stock]):
            return Response(
                {"detail": "Name, price, and stock are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the product
        product = Product.objects.create(
            name=name,
            price=price,
            stock=stock,
            is_active=is_active,
            company=request.user.company,
            created_by=request.user
        )
        
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsCompanyMember])
def toggle_product_active(request, pk):
    """
    Toggle product active status
    """
    try:
        product = Product.objects.get(pk=pk, company=request.user.company)
        product.is_active = not product.is_active
        product.save()
        
        return Response({
            'id': product.id,
            'is_active': product.is_active,
            'message': f'Product {product.name} is now {"active" if product.is_active else "inactive"}.'
        })
        
    except Product.DoesNotExist:
        return Response(
            {"detail": "Product not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_order(request):
    """
    Create a new order - Only admins can create orders
    """
    if not request.user.is_admin:
        return Response(
            {"detail": "Only admins can create orders"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        data = request.data if hasattr(request, 'data') else request.POST
        
        # Get the order data
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        if not product_id or not quantity or quantity <= 0:
            return Response(
                {"detail": "Valid product_id and quantity are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the product
        try:
            product = Product.objects.get(
                pk=product_id, 
                company=request.user.company,
                is_active=True
            )
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found or inactive"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check stock (but don't deduct yet - order is pending)
        if product.stock < quantity:
            return Response(
                {"detail": "Insufficient stock"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the order with PENDING status
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                product=product,
                quantity=quantity,
                company=request.user.company,
                created_by=request.user,
                status=Order.Status.PENDING
            )
            
            # Don't update stock or log email yet - order is pending
            # Stock will be deducted and email logged when status changes to SUCCESS
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )