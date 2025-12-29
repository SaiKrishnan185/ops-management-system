from django.db import models
from django.contrib.auth.models import User
from inventory.models import Product
from django.db import transaction

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
    
    def create_order(self, user=None):
        from inventory.models import Product

        with transaction.atomic():
            # Lock product row
            product = (
                Product.objects
                .select_for_update()
                .get(pk=self.product.pk)
            )

            if product.current_stock < self.quantity:
                raise ValueError("Insufficient stock to place order")

            # Deduct stock safely
            product.adjust_stock(   
                quantity=self.quantity,
                movement_type='OUT',
                user=user
            )

            self.status = 'IN_PROGRESS'
            self.save()
        
    def complete(self):
        if self.status != 'IN_PROGRESS':
            raise ValueError("Only in-progress orders can be completed")

        self.status = 'COMPLETED'
        self.save()


    def cancel(self, user=None):
        if self.status not in ['NEW', 'IN_PROGRESS']:
            raise ValueError("Only active orders can be cancelled")

        from inventory.models import Product

        with transaction.atomic():
            product = (
                Product.objects
                .select_for_update()
                .get(pk=self.product.pk)
            )

            # Return stock
            product.adjust_stock(
                quantity=self.quantity,
                movement_type='IN',
                user=user
            )

            self.status = 'CANCELLED'
            self.save()

