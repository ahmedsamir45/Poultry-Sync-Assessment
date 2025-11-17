from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
import csv
from .models import Company, CustomUser, Product, Order

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'company', 'created_by', 'is_active')
    list_filter = ('company', 'is_active')
    search_fields = ('name', 'company__name')
    actions = ['mark_inactive']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # If not superuser, filter companies and users
        if not request.user.is_superuser:
            # Only show the user's company
            form.base_fields['company'].queryset = Company.objects.filter(id=request.user.company_id)
            # Only show users from the same company
            form.base_fields['created_by'].queryset = CustomUser.objects.filter(company=request.user.company)
        return form
    
    def save_model(self, request, obj, form, change):
        # Set the current user as the creator if it's a new object
        if not change:
            obj.created_by = request.user
            # If user is not superuser, ensure the company is set to their company
            if not request.user.is_superuser:
                obj.company = request.user.company
        super().save_model(request, obj, form, change)
    
    def has_change_permission(self, request, obj=None):
        # Only allow changes to objects in the user's company
        if obj and not request.user.is_superuser:
            return obj.company == request.user.company
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        # Only allow deletion of objects in the user's company
        if obj and not request.user.is_superuser:
            return obj.company == request.user.company
        return super().has_delete_permission(request, obj)
    
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)
    mark_inactive.short_description = "Mark selected products as inactive"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'company', 'quantity', 'status', 'created_at', 'created_by']
    list_filter = ['company', 'status']
    actions = ['export_orders_csv']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # If not superuser, filter companies and users
        if not request.user.is_superuser:
            # Only show the user's company
            form.base_fields['company'].queryset = Company.objects.filter(id=request.user.company_id)
            # Only show products from the same company
            form.base_fields['product'].queryset = Product.objects.filter(company=request.user.company)
            # Only show users from the same company
            form.base_fields['created_by'].queryset = CustomUser.objects.filter(company=request.user.company)
        return form
    
    def save_model(self, request, obj, form, change):
        # Set the current user as the creator if it's a new object
        if not change:
            obj.created_by = request.user
            # If user is not superuser, ensure the company is set to their company
            if not request.user.is_superuser:
                obj.company = request.user.company
        super().save_model(request, obj, form, change)
    
    def has_change_permission(self, request, obj=None):
        # Only allow changes to objects in the user's company
        if obj and not request.user.is_superuser:
            return obj.company == request.user.company
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        # Only allow deletion of objects in the user's company
        if obj and not request.user.is_superuser:
            return obj.company == request.user.company
        return super().has_delete_permission(request, obj)
    
    def export_orders_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Product', 'Company', 'Quantity', 'Status', 'Created By', 'Created At'])
        
        for order in queryset:
            writer.writerow([
                order.id,
                order.product.name,
                order.company.name,
                order.quantity,
                order.get_status_display(),
                order.created_by.get_full_name() or order.created_by.username,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    export_orders_csv.short_description = "Export selected orders to CSV"

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Only show the user's company
        return qs.filter(id=request.user.company_id)
    
    def has_add_permission(self, request):
        # Only superusers can add companies
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        # Only allow changes to the user's own company or if superuser
        if obj and not request.user.is_superuser:
            return obj.id == request.user.company_id
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        # Prevent non-superusers from deleting companies
        if not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)
    
    def save_model(self, request, obj, form, change):
        # If user is not superuser, ensure they can only modify their own company
        if not request.user.is_superuser and hasattr(request.user, 'company'):
            if obj.id != request.user.company_id:
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied("You don't have permission to edit this company.")
        super().save_model(request, obj, form, change)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'company', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'company__name')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'company')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Role', {'fields': ('role',)}),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)
    
    def get_readonly_fields(self, request, obj=None):
        # Only superusers can change certain fields
        if not request.user.is_superuser:
            return ('is_superuser', 'is_staff', 'groups', 'user_permissions', 'last_login', 'date_joined')
        return super().get_readonly_fields(request, obj)
    
    def has_change_permission(self, request, obj=None):
        # Admins can edit users in their company
        if obj and request.user.is_admin:
            return obj.company == request.user.company
        # Only superusers can edit all users
        if not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deleting your own account
        if obj and obj == request.user:
            return False
        # Only superusers can delete users
        if not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)