from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg, F
from .models import Budget
from .serializers import BudgetSerializer

# Create your views here.


def index(request):
    if request.method == 'POST':
        return create_budget(request)
    

    user = request.user if request.user.is_authenticated else None
    
    if user:
        budgets = Budget.objects.filter(user=user).order_by('-created_at')
        queryset = Budget.objects.filter(user=user)
    else:
        budgets = []
        queryset = Budget.objects.none()
    
    # Calculate overview
    total_allocated = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
    total_spent = queryset.aggregate(total=Sum('spent_amount'))['total'] or 0
    active_budgets = queryset.filter(is_active=True).count()
    
    overview = {
        'total_allocated': total_allocated,
        'total_spent': total_spent,
        'total_remaining': total_allocated - total_spent,
        'active_budgets': active_budgets
    }
    
    context = {
        'budgets': budgets,
        'overview': overview,
    }
    return render(request, 'budgets/index.html', context)


def create_budget(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            budget = Budget.objects.create(
                user=request.user,
                name=request.POST.get('name'),
                period=request.POST.get('period'),
                total_amount=request.POST.get('total_amount'),
                category=request.POST.get('category'),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date'),
                description=request.POST.get('description', ''),
            )
            messages.success(request, 'Budget created successfully!')
        except Exception as e:
            messages.error(request, f'Error creating budget: {str(e)}')
    
    return redirect('budgets:index')


def edit_budget(request, budget_id):
    if not request.user.is_authenticated:
        return redirect('budgets:index')
    
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    
    if request.method == 'POST':
        try:
            budget.name = request.POST.get('name')
            budget.period = request.POST.get('period')
            budget.total_amount = request.POST.get('total_amount')
            budget.spent_amount = request.POST.get('spent_amount', budget.spent_amount)
            budget.category = request.POST.get('category')
            budget.start_date = request.POST.get('start_date')
            budget.end_date = request.POST.get('end_date')
            budget.description = request.POST.get('description', '')
            budget.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budgets:index')
        except Exception as e:
            messages.error(request, f'Error updating budget: {str(e)}')
    
    context = {'budget': budget}
    return render(request, 'budgets/edit.html', context)


def delete_budget(request, budget_id):
    if not request.user.is_authenticated:
        return redirect('budgets:index')
    
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted successfully!')
    
    return redirect('budgets:index')


# API views (existing)
class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get budget overview and statistics"""
        queryset = self.get_queryset()
        
        total_allocated = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        total_spent = queryset.aggregate(total=Sum('spent_amount'))['total'] or 0
        avg_usage = queryset.aggregate(avg=Avg('spent_amount'))['avg'] or 0
        
        active_budgets = queryset.filter(is_active=True).count()
        over_budget = queryset.filter(spent_amount__gt=F('total_amount')).count()
        
        return Response({
            'total_allocated': total_allocated,
            'total_spent': total_spent,
            'total_remaining': total_allocated - total_spent,
            'average_usage': avg_usage,
            'active_budgets': active_budgets,
            'over_budget_count': over_budget
        })
