from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('tasks/', views.my_tasks, name='my_tasks'),
    path('orders/', views.orders_view, name='orders'),
    path('payments/', views.payments_view, name='payments'),

    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/start/', views.start_task, name='start_task'),
    path('tasks/<int:pk>/complete/', views.complete_task, name='complete_task'),

]
