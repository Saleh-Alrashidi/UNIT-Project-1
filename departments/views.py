from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg
from .models import Department, Employee
from .serializers import DepartmentSerializer, EmployeeSerializer

# Create your views here.

# Template-based views
def index(request):
    # Get user or use anonymous user for demo
    user = request.user if request.user.is_authenticated else None
    
    if user:
        departments = Department.objects.filter(user=user).order_by('name')
        employees = Employee.objects.filter(department__user=user).order_by('name')
        dept_queryset = Department.objects.filter(user=user)
        employees_queryset = Employee.objects.filter(department__user=user)
    else:
        departments = Department.objects.none()
        employees = Employee.objects.none()
        dept_queryset = Department.objects.none()
        employees_queryset = Employee.objects.none()
    
    # Calculate overview
    total_budget = dept_queryset.aggregate(total=Sum('budget_allocated'))['total'] or 0
    total_used = dept_queryset.aggregate(total=Sum('budget_used'))['total'] or 0
    total_employees = employees_queryset.filter(is_active=True).count()
    avg_salary = employees_queryset.filter(is_active=True).aggregate(avg=Avg('salary'))['avg'] or 0
    
    # Add employee_count to each department
    for department in departments:
        department.employee_count = department.employees.filter(is_active=True).count()
    
    overview = {
        'total_departments': dept_queryset.count(),
        'active_departments': dept_queryset.filter(is_active=True).count(),
        'total_budget_allocated': total_budget,
        'total_budget_used': total_used,
        'total_budget_remaining': total_budget - total_used,
        'total_employees': total_employees,
        'average_salary': avg_salary
    }
    
    context = {
        'departments': departments,
        'employees': employees,
        'overview': overview,
    }
    return render(request, 'departments/index.html', context)


def create_department(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            department = Department.objects.create(
                user=request.user,
                name=request.POST.get('name'),
                manager=request.POST.get('manager', ''),
                budget_allocated=request.POST.get('budget_allocated', 0),
                budget_used=request.POST.get('budget_used', 0),
                description=request.POST.get('description', ''),
            )
            messages.success(request, 'Department created successfully!')
        except Exception as e:
            messages.error(request, f'Error creating department: {str(e)}')
    
    return redirect('departments:index')


def edit_department(request, dept_id):
    if not request.user.is_authenticated:
        return redirect('departments:index')
    
    department = get_object_or_404(Department, id=dept_id, user=request.user)
    
    if request.method == 'POST':
        try:
            department.name = request.POST.get('name')
            department.manager = request.POST.get('manager', '')
            department.budget_allocated = request.POST.get('budget_allocated', 0)
            department.budget_used = request.POST.get('budget_used', department.budget_used)
            department.description = request.POST.get('description', '')
            department.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('departments:index')
        except Exception as e:
            messages.error(request, f'Error updating department: {str(e)}')
    
    context = {'department': department}
    return render(request, 'departments/edit_department.html', context)


def delete_department(request, dept_id):
    if not request.user.is_authenticated:
        return redirect('departments:index')
    
    department = get_object_or_404(Department, id=dept_id, user=request.user)
    
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted successfully!')
    
    return redirect('departments:index')


def create_employee(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            department = get_object_or_404(Department, id=request.POST.get('department'), user=request.user)
            employee = Employee.objects.create(
                department=department,
                name=request.POST.get('name'),
                position=request.POST.get('position'),
                salary=request.POST.get('salary'),
                hire_date=request.POST.get('hire_date'),
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone', ''),
            )
            messages.success(request, 'Employee added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding employee: {str(e)}')
    
    return redirect('departments:index')


def edit_employee(request, emp_id):
    if not request.user.is_authenticated:
        return redirect('departments:index')
    
    employee = get_object_or_404(Employee, id=emp_id, department__user=request.user)
    
    if request.method == 'POST':
        try:
            employee.name = request.POST.get('name')
            employee.position = request.POST.get('position')
            employee.salary = request.POST.get('salary')
            employee.hire_date = request.POST.get('hire_date')
            employee.email = request.POST.get('email', '')
            employee.phone = request.POST.get('phone', '')
            employee.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('departments:index')
        except Exception as e:
            messages.error(request, f'Error updating employee: {str(e)}')
    
    context = {'employee': employee}
    return render(request, 'departments/edit_employee.html', context)


def delete_employee(request, emp_id):
    if not request.user.is_authenticated:
        return redirect('departments:index')
    
    employee = get_object_or_404(Employee, id=emp_id, department__user=request.user)
    
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
    
    return redirect('departments:index')


# API views (existing)
class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Department.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get department overview and statistics"""
        queryset = self.get_queryset()
        
        total_budget = queryset.aggregate(total=Sum('budget_allocated'))['total'] or 0
        total_used = queryset.aggregate(total=Sum('budget_used'))['total'] or 0
        total_employees = Employee.objects.filter(
            department__in=queryset, 
            is_active=True
        ).count()
        avg_salary = Employee.objects.filter(
            department__in=queryset,
            is_active=True
        ).aggregate(avg=Avg('salary'))['avg'] or 0
        
        return Response({
            'total_departments': queryset.count(),
            'active_departments': queryset.filter(is_active=True).count(),
            'total_budget_allocated': total_budget,
            'total_budget_used': total_used,
            'total_budget_remaining': total_budget - total_used,
            'total_employees': total_employees,
            'average_salary': avg_salary
        })


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Employee.objects.filter(department__user=self.request.user)
