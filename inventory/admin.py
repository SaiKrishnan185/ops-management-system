from django.contrib import admin
from .models import Product, StockMovement

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    readonly_fields = ('current_stock',)

    list_display = ('name', 'current_stock', 'reorder_level', 'price')

    def has_change_permission(self, request, obj=None):
        return True


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'quantity',
        'movement_type',
        'created_at',
        'performed_by',
    )
    
    readonly_fields = (
        'performed_by',
        'created_at',
    )


    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def save_model(self, request, obj, form, change):
        """
        Automatically record who performed the stock movement.
        """
        if not obj.pk:
            obj.performed_by = request.user
        super().save_model(request, obj, form, change)
