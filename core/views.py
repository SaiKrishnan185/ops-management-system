from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from orders.models import Order
from tasks.models import Task
from payments.models import Payment
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from core.utils import order_metrics, task_metrics


@login_required
def dashboard(request):
    context = {}

    if request.user.is_superuser:
        context.update(order_metrics())
        context.update(task_metrics())
        return render(request, 'core/admin_dashboard.html', context)

    context.update(task_metrics(user=request.user))
    return render(request, 'core/staff_dashboard.html', context)



def user_login(request):
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
    orders = Order.objects.all()
    return render(request, 'core/orders.html', {'orders': orders})


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