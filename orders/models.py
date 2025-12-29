from django.db import models, transaction
from django.contrib.auth.models import User
from inventory.models import Product
from decimal import Decimal
from django.db.models import Sum


class Order(models.Model):

    STATUS_CHOICES = (
        ('NEW', 'New'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    customer_name = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NEW'
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

    # -----------------------------
    # ORDER CREATION (SINGLE SOURCE OF TRUTH)
    # -----------------------------
    def create_order(self, user=None):
        """
        1. Reserve stock
        2. Create tasks from templates
        3. Status remains NEW until tasks move it forward
        """
        from tasks.models import TaskTemplate, Task

        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=self.product.pk)

            if product.current_stock < self.quantity:
                raise ValueError("Insufficient stock to place order")

            # Reserve stock
            product.adjust_stock(
                quantity=self.quantity,
                movement_type='OUT',
                user=user
            )

            self.status = 'NEW'
            self.save()

            # Auto-create tasks
            templates = (
                TaskTemplate.objects
                .filter(product=self.product)
                .order_by('order_sequence')
            )

            for template in templates:
                Task.objects.create(
                    title=template.title,
                    order=self
                )

    # -----------------------------
    # PAYMENTS
    # -----------------------------
    def total_paid(self):
        return (
            self.payments.aggregate(total=Sum('amount'))['total']
            or Decimal('0.00')
        )

    def total_amount(self):
        return self.quantity * self.product.price
    
    def outstanding_amount(self):
        return self.total_amount() - self.total_paid()

    # -----------------------------
    # CANCELLATION
    # -----------------------------
    def cancel(self, user=None):
        if self.status == 'COMPLETED':
            raise ValueError("Completed orders cannot be cancelled")

        if self.status == 'CANCELLED':
            return  # Idempotent

        with transaction.atomic():
            Order.objects.select_for_update().get(pk=self.pk)
            product = Product.objects.select_for_update().get(pk=self.product.pk)

            # Return stock
            product.adjust_stock(
                quantity=self.quantity,
                movement_type='IN',
                user=user
            )

            # Refund if needed
            self.refund_order(user=user)

            # Delete tasks
            self.tasks.all().delete()

            self.status = 'CANCELLED'
            self.save()

    # -----------------------------
    # REFUNDS
    # -----------------------------
    def refund_order(self, user=None):
        from payments.models import Payment

        if Payment.objects.filter(
            order=self,
            payment_mode='REFUND'
        ).exists():
            return

        total_paid = self.total_paid()
        if total_paid <= Decimal('0.00'):
            return

        Payment.objects.create(
            order=self,
            amount=-total_paid,
            payment_mode='REFUND',
            received_by=user,
            notes='Order cancelled – refund issued'
        )
