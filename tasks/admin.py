from django.contrib import admin
from .models import Task, TaskTemplate
from orders.models import Order


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'order',
        'assigned_to',
        'status',
        'due_date',
        'created_at',
    )

    list_filter = ('status', 'due_date')
    search_fields = ('title',)

    readonly_fields = ('status',)

    actions = ['mark_completed']

    def mark_completed(self, request, queryset):
        for task in queryset:
            try:
                task.complete()
            except ValueError as e:
                self.message_user(request, str(e), level='ERROR')

    mark_completed.short_description = "Mark selected tasks as completed (safe)"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Show only active orders when assigning tasks.
        """
        if db_field.name == "order":
            kwargs["queryset"] = Order.objects.exclude(
                status__in=['CANCELLED', 'COMPLETED']
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        """
        Show detailed order info in dropdown.
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
    
    
@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'order_sequence')
    ordering = ('product', 'order_sequence')