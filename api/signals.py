from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
import logging
from .models import Order

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, created, **kwargs):
    if instance.status == Order.Status.SUCCESS:
        # Log confirmation email (simulated)
        logger.info(
            f"ORDER CONFIRMATION: Order #{instance.id} - "
            f"Product: {instance.product.name}, "
            f"Quantity: {instance.quantity}, "
            f"Total: {instance.quantity * instance.product.price}, "
            f"Customer: {instance.created_by.username if instance.created_by else 'Unknown'}"
        )
        
        # Deduct stock
        if instance.validate_stock():
            instance.product.stock -= instance.quantity
            instance.product.save()