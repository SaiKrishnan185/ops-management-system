from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer_name',
        'product',
        'quantity',
        'status',
        'assigned_to',
        'created_at',
    )

    list_filter = ('status', 'product')
    search_fields = ('customer_name',)

    # -----------------------------
    # READ-ONLY CONTROL
    # -----------------------------
    def get_readonly_fields(self, request, obj=None):
        """
        Once an order exists, critical fields become immutable.
        """
        if obj:
            return (
                'product',
                'quantity',
                'customer_name',
                'status',
                'created_at',
            )
        return ()

    # -----------------------------
    # PERMISSION CONTROL
    # -----------------------------
    def has_change_permission(self, request, obj=None):
        """
        Completed or cancelled orders are fully locked.
        """
        if obj and obj.status in ['COMPLETED', 'CANCELLED']:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        """
        Orders should never be deleted once created.
        """
        return False

    # -----------------------------
    # SAVE LOGIC (CRITICAL)
    # -----------------------------
    def save_model(self, request, obj, form, change):
        """
        Force all new orders to go through business logic.
        """
        if not change:
            # NEW ORDER → must deduct stock safely
            try:
                obj.create_order(user=request.user)
            except ValueError as e:
                raise ValidationError(str(e))
        else:
            # Existing order → no stock logic here
            super().save_model(request, obj, form, change)

    # -----------------------------
    # ADMIN ACTION: CANCEL ORDER
    # -----------------------------
    actions = ['cancel_order']

    def cancel_order(self, request, queryset):
        """
        Admin-safe cancellation using business logic.
        """
        for order in queryset:
            try:
                order.cancel(user=request.user)
            except ValueError as e:
                self.message_user(request, str(e), level='ERROR')

    cancel_order.short_description = "Cancel selected orders (safe)"
