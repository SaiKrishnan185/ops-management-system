from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from orders.models import Order
from django.utils import timezone


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
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    # -----------------------------
    # BUSINESS VALIDATION
    # -----------------------------
    def clean(self):
        if self.order and self.order.status in ['CANCELLED', 'COMPLETED']:
            raise ValidationError(
                "Cannot assign tasks to cancelled or completed orders."
            )

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        self.full_clean()
        super().save(*args, **kwargs)

        # First task → Order becomes IN_PROGRESS
        if is_new and self.order and self.order.status == 'NEW':
            self.order.status = 'IN_PROGRESS'
            self.order.save(update_fields=['status'])

    # -----------------------------
    # WORKFLOW METHODS
    # -----------------------------
    def start(self):
        if self.status != 'PENDING':
            raise ValueError("Only pending tasks can be started")

        self.status = 'IN_PROGRESS'
        self.save()

    def complete(self):
        if self.status != 'IN_PROGRESS':
            raise ValueError("Only in-progress tasks can be completed")

        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save()

        if self.order:
            remaining = self.order.tasks.exclude(status='COMPLETED').exists()
            if not remaining:
                self.order.status = 'COMPLETED'
                self.order.save(update_fields=['status'])

class TaskTemplate(models.Model):
    title = models.CharField(max_length=200)
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE,
        related_name='task_templates'
    )
    order_sequence = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} → {self.title}"
    