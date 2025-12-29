from django.db import models, transaction
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    current_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,default=0)

    def __str__(self):
        return f"{self.name} ({self.current_stock})"
    
    def adjust_stock(self, quantity, movement_type, user=None):
        with transaction.atomic():
        # Lock the product row
            product = (
                Product.objects
                .select_for_update()
                .get(pk=self.pk)
            )

            if movement_type == 'OUT':
                if product.current_stock < quantity:
                    raise ValueError("Insufficient stock")

                product.current_stock -= quantity

            elif movement_type == 'IN':
                product.current_stock += quantity

            product.save()

            StockMovement.objects.create(
                product=product,
                quantity=quantity,
                movement_type=movement_type,
                performed_by=user
            )
        self.refresh_from_db()


class StockMovement(models.Model):
    STOCK_TYPE = (
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=3, choices=STOCK_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"
