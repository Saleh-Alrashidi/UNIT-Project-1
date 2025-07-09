from django.contrib import admin
from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'period', 'total_amount', 'spent_amount', 'remaining_amount', 'is_active')
    list_filter = ('period', 'is_active', 'created_at')
    search_fields = ('name', 'category', 'description')
    readonly_fields = ('created_at', 'updated_at', 'remaining_amount', 'percentage_used')
    ordering = ('-created_at',)
