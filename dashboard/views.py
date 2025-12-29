from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db.models import Count, Sum, Q
from decimal import Decimal
from django.db import models


from orders.models import Order
from inventory.models import Product
from tasks.models import Task
from payments.models import Payment

from accounts.permissions import admin_required, staff_required




@login_required
def admin_dashboard(request):
    admin_required(request.user)
    today = now().date()

    context = {
        # Orders
        'total_orders': Order.objects.count(),
        'orders_today': Order.objects.filter(created_at__date=today).count(),
        'delayed_orders': Order.objects.filter(
            status='IN_PROGRESS',
            created_at__date__lt=today
        ).count(),

        # Inventory
        'low_stock_products': Product.objects.filter(
            current_stock__lt=models.F('reorder_level')
        ),

        # Tasks
        'pending_tasks': Task.objects.filter(status='PENDING').count(),
        'overdue_tasks': Task.objects.filter(
            due_date__lt=today,
            status__in=['PENDING', 'IN_PROGRESS']
        ).count(),

        # Payments
        'total_received': Payment.objects.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00'),
    }

    return render(request, 'dashboard/admin_dashboard.html', context)




@login_required
def staff_dashboard(request):
    staff_required(request.user)

    user = request.user
    today = now().date()

    context = {
        'my_tasks': Task.objects.filter(
            assigned_to=user,
            status__in=['PENDING', 'IN_PROGRESS']
        ),

        'overdue_tasks': Task.objects.filter(
            assigned_to=user,
            due_date__lt=today,
            status__in=['PENDING', 'IN_PROGRESS']
        ),

        'my_orders': Order.objects.filter(
            assigned_to=user,
            status='IN_PROGRESS'
        ),
    }

    return render(request, 'dashboard/staff_dashboard.html', context)
