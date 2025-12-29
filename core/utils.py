from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from tasks.models import Task
from django.utils import timezone

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