from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, EmployeeViewSet, index, create_department, 
    edit_department, delete_department, create_employee, edit_employee, delete_employee
)

app_name = 'departments'

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    # Template-based views
    path('', index, name='index'),
    
    # Department views
    path('department/create/', create_department, name='create_department'),
    path('department/edit/<int:dept_id>/', edit_department, name='edit_department'),
    path('department/delete/<int:dept_id>/', delete_department, name='delete_department'),
    
    # Employee views
    path('employee/create/', create_employee, name='create_employee'),
    path('employee/edit/<int:emp_id>/', edit_employee, name='edit_employee'),
    path('employee/delete/<int:emp_id>/', delete_employee, name='delete_employee'),
    
    # API endpoints
    path('api/', include(router.urls)),
]