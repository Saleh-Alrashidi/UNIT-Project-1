from django.db import models
from django.contrib.auth.models import User


class FinanceRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='finance_records')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('income', 'Income'),
            ('expense', 'Expense'),
            ('transfer', 'Transfer'),
        ]
    )
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.amount}"
