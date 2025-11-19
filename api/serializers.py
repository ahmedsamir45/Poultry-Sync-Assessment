from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Product, Order
from django.utils import timezone
from django.db import transaction


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'company', 'company_name', 'is_active', 'date_joined']
        read_only_fields = ['date_joined', 'is_active']
        
        # extra_kwargs:write_only read_only required default allow_null
        
        extra_kwargs = {
            'password': {'write_only': True},
            'company': {'required': False}
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', User.Role.VIEWER),
            company=validated_data.get('company')
        )
        return user

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'is_active', 'created_at']
        read_only_fields = ['created_at']

class OrderSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(source='product.name', read_only=True)
    # because the name fieled not exist in the order model
    class Meta:
        model = Order
        fields = ['id', 'product', 'product_name', 'quantity', 'status', 'created_at', 'shipped_at']
        read_only_fields = ['created_at', 'shipped_at']

    def validate(self, data):
        user = self.context['request'].user
        
        # For creation, validate product and quantity
        if self.instance is None:  # Creating new order
            if not user.is_admin:
                raise serializers.ValidationError("Only admins can create orders")
            
            product = data.get('product')
            quantity = data.get('quantity')
            
            if product and product.company != user.company:
                raise serializers.ValidationError("Product not found in your company")
            
            if product and quantity and not product.can_be_ordered(quantity):
                raise serializers.ValidationError("Insufficient stock or product inactive")
        
        # For updates, validate quantity if product is being changed
        else:  # Updating existing order
            product = data.get('product', self.instance.product)
            quantity = data.get('quantity', self.instance.quantity)
            
            if product and product.company != user.company:
                raise serializers.ValidationError("Product not found in your company")
        
        return data

    def create(self, validated_data):
        validated_data['company'] = self.context['request'].user.company
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Handle status change - when status becomes SUCCESS
        old_status = instance.status
        new_status = validated_data.get('status', instance.status)
        
        if new_status == Order.Status.SUCCESS:
          
            # Set shipped_at if not already set
            if not instance.shipped_at:
                instance.shipped_at = timezone.now()
            
            # If status is changing from non-SUCCESS to SUCCESS, deduct stock and log email
            if old_status != Order.Status.SUCCESS:
                with transaction.atomic():
                    # Deduct stock
                    product = instance.product
                    if product.stock >= instance.quantity:
                        product.stock -= instance.quantity
                        product.save()
                    else:
                        raise serializers.ValidationError("Insufficient stock to fulfill order")
                    
                    # Email logging will be handled in the view after save
        
        return super().update(instance, validated_data)