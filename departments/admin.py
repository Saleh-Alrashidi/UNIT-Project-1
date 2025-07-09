from django.contrib import admin
from .models import Department, Employee


class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'manager', 'budget_allocated', 'budget_used', 'budget_remaining', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'manager', 'description')
    readonly_fields = ('created_at', 'updated_at', 'budget_remaining', 'budget_percentage_used')
    inlines = [EmployeeInline]
    ordering = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'position', 'salary', 'hire_date', 'is_active')
    list_filter = ('department', 'position', 'is_active', 'hire_date')
    search_fields = ('name', 'position', 'email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
