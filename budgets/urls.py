from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BudgetViewSet, index, create_budget, edit_budget, delete_budget

app_name = 'budgets'

router = DefaultRouter()
router.register(r'budgets', BudgetViewSet, basename='budget')

urlpatterns = [
    path('', index, name='index'),
    path('create/', create_budget, name='create'),
    path('edit/<int:budget_id>/', edit_budget, name='edit'),
    path('delete/<int:budget_id>/', delete_budget, name='delete'),
    path('api/', include(router.urls)),
]