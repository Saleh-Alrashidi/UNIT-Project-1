from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    budget_allocated = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    budget_used = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    manager = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def budget_remaining(self):
        return self.budget_allocated - self.budget_used

    @property
    def budget_percentage_used(self):
        if self.budget_allocated > 0:
            return (self.budget_used / self.budget_allocated) * 100
        return 0


class Employee(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    hire_date = models.DateField()
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.position}"
