from django.contrib import admin
from .models import FinanceRecord


@admin.register(FinanceRecord)
class FinanceRecordAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'amount', 'transaction_type', 'category', 'date')
    list_filter = ('transaction_type', 'category', 'date', 'created_at')
    search_fields = ('title', 'description', 'category')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-date', '-created_at')
