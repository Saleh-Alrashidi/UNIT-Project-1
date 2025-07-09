from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import FinanceRecord
from .serializers import FinanceRecordSerializer


# Template-based views
def index(request):
    if request.method == 'POST':
        return create_record(request)
    
    # Get user or use anonymous user for demo
    user = request.user if request.user.is_authenticated else None
    
    if user:
        records = FinanceRecord.objects.filter(user=user).order_by('-date', '-created_at')[:20]
        user_records = FinanceRecord.objects.filter(user=user)
    else:
        records = []
        user_records = FinanceRecord.objects.none()
    
    # Calculate summary
    total_income = user_records.filter(transaction_type='income').aggregate(
        total=Sum('amount'))['total'] or 0
    total_expenses = user_records.filter(transaction_type='expense').aggregate(
        total=Sum('amount'))['total'] or 0
    
    summary = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': total_income - total_expenses,
    }
    
    context = {
        'records': records,
        'summary': summary,
    }
    return render(request, 'finance_records/index.html', context)


def create_record(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            record = FinanceRecord.objects.create(
                user=request.user,
                title=request.POST.get('title'),
                amount=request.POST.get('amount'),
                transaction_type=request.POST.get('transaction_type'),
                category=request.POST.get('category'),
                date=request.POST.get('date'),
                description=request.POST.get('description', ''),
            )
            messages.success(request, 'Finance record created successfully!')
        except Exception as e:
            messages.error(request, f'Error creating record: {str(e)}')
    
    return redirect('finance_records:index')


def edit_record(request, record_id):
    if not request.user.is_authenticated:
        return redirect('finance_records:index')
    
    record = get_object_or_404(FinanceRecord, id=record_id, user=request.user)
    
    if request.method == 'POST':
        try:
            record.title = request.POST.get('title')
            record.amount = request.POST.get('amount')
            record.transaction_type = request.POST.get('transaction_type')
            record.category = request.POST.get('category')
            record.date = request.POST.get('date')
            record.description = request.POST.get('description', '')
            record.save()
            messages.success(request, 'Finance record updated successfully!')
            return redirect('finance_records:index')
        except Exception as e:
            messages.error(request, f'Error updating record: {str(e)}')
    
    context = {'record': record}
    return render(request, 'finance_records/edit.html', context)


def delete_record(request, record_id):
    if not request.user.is_authenticated:
        return redirect('finance_records:index')
    
    record = get_object_or_404(FinanceRecord, id=record_id, user=request.user)
    
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Finance record deleted successfully!')
    
    return redirect('finance_records:index')


# API views (existing)
class FinanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = FinanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FinanceRecord.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get financial summary for the user"""
        queryset = self.get_queryset()
        
        total_income = queryset.filter(transaction_type='income').aggregate(
            total=Sum('amount'))['total'] or 0
        total_expenses = queryset.filter(transaction_type='expense').aggregate(
            total=Sum('amount'))['total'] or 0
        
        return Response({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': total_income - total_expenses,
            'total_records': queryset.count()
        })

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get records grouped by category"""
        queryset = self.get_queryset()
        
        categories = queryset.values('category').annotate(
            total_amount=Sum('amount'),
            count=Count('id')
        ).order_by('-total_amount')
        
        return Response(categories)
