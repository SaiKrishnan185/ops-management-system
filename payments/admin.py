from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    readonly_fields = ('received_at',)

    def has_change_permission(self, request, obj=None):
        return False  # No edits allowed

    def has_delete_permission(self, request, obj=None):
        return False  # No deletes allowed
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Show only payable orders.
        """
        from orders.models import Order
        if db_field.name == "order":
            kwargs["queryset"] = Order.objects.filter(
                status__in=['NEW', 'IN_PROGRESS', 'COMPLETED']
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        """
        Show detailed order info in payment dropdown.
        """
        form = super().get_form(request, obj, **kwargs)

        form.base_fields['order'].label_from_instance = (
            lambda order: (
                f"Order #{order.id} | "
                f"{order.customer_name} | "
                f"{order.product.name} x {order.quantity} | "
                f"{order.status}"
            )
        )

        return form