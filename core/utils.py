from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from tasks.models import Task
from django.utils import timezone
import json
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.db.models import Sum
from payments.models import Payment
from decimal import Decimal
from collections import OrderedDict

def order_metrics():
    today = timezone.now().date()
    week_start = today - timedelta(days=7)

    return {
        "orders_today": Order.objects.filter(created_at__date=today).count(),
        "orders_week": Order.objects.filter(created_at__date__gte=week_start).count(),
        "orders_pending": Order.objects.filter(
            status__in=['NEW', 'IN_PROGRESS']
        ).count(),
    }


def task_metrics(user=None):
    today = timezone.now().date()

    qs = Task.objects.all()
    if user:
        qs = qs.filter(assigned_to=user)

    return {
        "tasks_pending": qs.exclude(status='COMPLETED').count(),
        "tasks_completed_today": qs.filter(
            status='COMPLETED',
            completed_at__date=today
        ).count(),
    }

def admin_chart_data():
    today = timezone.now().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    day_map = OrderedDict((d.strftime("%d %b"), 0) for d in days)

    orders = (
        Order.objects
        .filter(created_at__date__gte=days[0])
        .values('created_at__date')
        .annotate(count=Count('id'))
    )

    for o in orders:
        label = o['created_at__date'].strftime("%d %b")
        day_map[label] = o['count']

    # TASK STATUS
    status_map = {
        'PENDING': 0,
        'IN_PROGRESS': 0,
        'COMPLETED': 0,
    }

    task_stats = Task.objects.values('status').annotate(count=Count('id'))
    for t in task_stats:
        status_map[t['status']] = t['count']

    return {
        "order_labels": list(day_map.keys()),
        "order_counts": list(day_map.values()),
        "task_labels": list(status_map.keys()),
        "task_counts": list(status_map.values()),
    }

def weekly_comparison():
    today = timezone.now().date()

    this_week_start = today - timedelta(days=today.weekday())
    last_week_start = this_week_start - timedelta(days=7)
    last_week_end = this_week_start - timedelta(days=1)

    this_week_orders = Order.objects.filter(
        created_at__date__gte=this_week_start
    ).count()

    last_week_orders = Order.objects.filter(
        created_at__date__range=(last_week_start, last_week_end)
    ).count()

    change = this_week_orders - last_week_orders
    percent = (
        (change / last_week_orders) * 100
        if last_week_orders > 0 else 100
    )

    return {
        "this_week_orders": this_week_orders,
        "last_week_orders": last_week_orders,
        "week_change": change,
        "week_percent": round(percent, 1),
    }

def payment_summary():
    today = timezone.now().date()
    week_start = today - timedelta(days=6)

    payments_today = Payment.objects.filter(
        received_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    payments_week = Payment.objects.filter(
        received_at__date__gte=week_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    refunds = Payment.objects.filter(
        payment_mode='REFUND'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    outstanding = Decimal('0.00')
    for order in Order.objects.exclude(status='CANCELLED'):
        outstanding += max(order.outstanding_amount(), Decimal('0.00'))

    net_revenue = payments_week + refunds  # refunds are negative

    return {
        "payments_today": payments_today,
        "payments_week": payments_week,
        "refunds_total": abs(refunds),
        "net_revenue": net_revenue,
        "outstanding_amount": outstanding,
    }
    

def staff_task_charts(user):
    today = timezone.now().date()

    # TASK STATUS
    status_data = (
        Task.objects
        .filter(assigned_to=user)
        .values('status')
        .annotate(count=Count('id'))
    )

    task_status_labels = [s['status'] for s in status_data]
    task_status_counts = [s['count'] for s in status_data]

    # PENDING vs OVERDUE
    pending_count = Task.objects.filter(
        assigned_to=user,
        status__in=['PENDING', 'IN_PROGRESS'],
        due_date__gte=today
    ).count()

    overdue_count = Task.objects.filter(
        assigned_to=user,
        status__in=['PENDING', 'IN_PROGRESS'],
        due_date__lt=today
    ).count()

    return {
        "task_status_labels": task_status_labels,
        "task_status_counts": task_status_counts,
        "overdue_labels": ["Pending", "Overdue"],
        "overdue_counts": [pending_count, overdue_count],
    }

def tasks_due_today(user):
    today = timezone.now().date()

    due_today = Task.objects.filter(
        assigned_to=user,
        status__in=['PENDING', 'IN_PROGRESS'],
        due_date=today
    )

    overdue = Task.objects.filter(
        assigned_to=user,
        status__in=['PENDING', 'IN_PROGRESS'],
        due_date__lt=today
    )

    return {
        "tasks_due_today_count": due_today.count(),
        "tasks_due_today_list": due_today.order_by('due_date')[:5],
        "tasks_overdue_count": overdue.count(),
    }