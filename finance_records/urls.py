from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinanceRecordViewSet, index, create_record, edit_record, delete_record

app_name = 'finance_records'

router = DefaultRouter()
router.register(r'records', FinanceRecordViewSet, basename='financerecord')

urlpatterns = [
    # Template-based views
    path('', index, name='index'),
    path('create/', create_record, name='create'),
    path('edit/<int:record_id>/', edit_record, name='edit'),
    path('delete/<int:record_id>/', delete_record, name='delete'),
    
    # API endpoints
    path('api/', include(router.urls)),
]