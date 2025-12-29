from django.db import models
from django.contrib.auth.models import User
from orders.models import Order
from django.db.models import Sum
from decimal import Decimal

class Payment(models.Model):

    PAYMENT_MODE_CHOICES = (
        ('CASH', 'Cash'),
        ('UPI', 'UPI'),
        ('BANK', 'Bank Transfer'),
        ('CARD', 'Card'),
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name='payments'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_mode = models.CharField(
        max_length=10,
        choices=PAYMENT_MODE_CHOICES
    )

    received_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    received_at = models.DateTimeField(auto_now_add=True)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Payment {self.amount} for Order #{self.order.id}"
    

    def total_paid(self):
        return self.payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')


    def outstanding_amount(self):
        return self.total_amount() - self.total_paid()
    
    def total_paid(self):
        return self.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')


    def outstanding_amount(self):
        return self.total_amount() - self.total_paid()
