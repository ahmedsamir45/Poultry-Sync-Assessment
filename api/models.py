from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


import uuid

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        OPERATOR = 'operator', 'Operator'
        VIEWER = 'viewer', 'Viewer'

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)

    def __str__(self):
        role_name = self.get_role_display()
        return f"{self.username} ({role_name} - {self.company.name})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_operator(self):
        return self.role == self.Role.OPERATOR

    @property
    def is_viewer(self):
        return self.role == self.Role.VIEWER

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def soft_delete(self):
        self.is_active = False
        self.save()

    def can_be_ordered(self, quantity):
        return self.is_active and self.stock >= quantity

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    shipped_at = models.DateTimeField(null=True, blank=True) # we should add completed at here

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.product.name}"

    def save(self, *args, **kwargs):
        if self.status == self.Status.SUCCESS and not self.shipped_at:
            self.shipped_at = timezone.now()
        super().save(*args, **kwargs)

    def can_user_edit(self, user):
        if user.is_admin:
            return True
        if user.is_operator:
            # Operators can edit orders created today (regardless of who created them)
            return self.created_at.date() == timezone.now().date()
        return False

    def validate_stock(self):
        return self.product.stock >= self.quantity
    
from django.db.models.signals import post_save
from django.dispatch import receiver




@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, created, **kwargs):
    

    
    # Deduct stock
    if instance.validate_stock():
        instance.product.stock -= instance.quantity
        instance.product.save()