from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from inventory.models import Product
from orders.models import Order
from tasks.models import Task
from payments.models import Payment
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from core.utils import order_metrics, task_metrics, admin_chart_data, weekly_comparison, payment_summary, staff_task_charts, tasks_due_today


from django.http import HttpResponse
from django.contrib.auth.models import User
import os

def bootstrap_admin(request):
    if os.getenv("ALLOW_BOOTSTRAP") != "1":
        return HttpResponse("Disabled", status=403)

    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            "admin",
            "saikrishnan187@gmail.com",
            "Demo@123"
        )
        return HttpResponse("Admin created")

    return HttpResponse("Admin already exists")

@login_required
def dashboard(request):
    context = {}

    if request.user.is_superuser:
        context.update(order_metrics())
        context.update(task_metrics())
        context.update(admin_chart_data())
        context.update(weekly_comparison())
        context.update(payment_summary())

        outstanding_orders = [
        o for o in Order.objects.exclude(status='CANCELLED')
        if o.outstanding_amount() > 0]

        context["outstanding_orders"] = outstanding_orders

        return render(request, 'core/admin_dashboard.html', context)

    context.update(task_metrics(user=request.user))
    context.update(staff_task_charts(request.user))
    context.update(tasks_due_today(request.user))
    
    return render(request, 'core/staff_dashboard.html', context)



def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('dashboard')

        return render(request, 'core/login.html', {'error': 'Invalid credentials'})

    return render(request, 'core/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')



@login_required
def my_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, 'core/tasks.html', {'tasks': tasks})


@login_required
def orders_view(request):
    sort = request.GET.get("sort", "-created_at")

    allowed_sorts = [
        "created_at", "-created_at",
        "status", "-status",
        "customer_name", "-customer_name",
        "assigned_to__username", "-assigned_to__username",
    ]

    if sort not in allowed_sorts:
        sort = "-created_at"

    orders = Order.objects.select_related(
        "product", "assigned_to"
    ).order_by(sort)

    return render(
        request,
        "core/orders.html",
        {
            "orders": orders,
            "current_sort": sort
        }
    )


@login_required
def payments_view(request):
    payments = Payment.objects.all()
    return render(request, 'core/payments.html', {'payments': payments})


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if task.assigned_to != request.user and not request.user.is_superuser:
        return HttpResponseForbidden()

    return render(request, 'core/task_detail.html', {'task': task})


@login_required
def start_task(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if task.assigned_to != request.user:
        return HttpResponseForbidden()

    task.start()
    return redirect('task_detail', pk=pk)


@login_required
def complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if task.assigned_to != request.user:
        return HttpResponseForbidden()

    task.complete()
    return redirect('task_detail', pk=pk)

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_products(request):
    products = Product.objects.all().order_by("name")
    return render(request, "core/admin_products.html", {
        "products": products
    })