from django.db import models
from django.contrib.auth.models import User
from orders.models import Order

class Task(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    )

    title = models.CharField(max_length=200)

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    due_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

    def start(self):
        if self.status != 'PENDING':
            raise ValueError("Only pending tasks can be started")

        self.status = 'IN_PROGRESS'
        self.save()


    def complete(self):
        if self.status != 'IN_PROGRESS':
            raise ValueError("Only in-progress tasks can be completed")

        self.status = 'COMPLETED'
        self.save()

