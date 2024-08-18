from django.urls import path
from .views import group_list
from .views import  GroupDetailView, create_group, dashboard, expense_list, create_expense, payment_list, create_payment, settle_payment
from .views import export_payments_csv
urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('groups/', group_list, name='group_list'),
    path('groups/<int:group_id>/', GroupDetailView, name='group_detail'),
    path('export_payments_csv/', export_payments_csv, name='export_payments_csv'),
    path('groups/create/', create_group, name='create_group'),
    path('expenses/', expense_list, name='expense_list'),
    path('expenses/create/', create_expense, name='create_expense'),
    path('payments/', payment_list, name='payment_list'),
    path('payments/create/', create_payment, name='create_payment'),
    path('payments/settle/<int:payment_id>/', settle_payment, name='settle_payment'),
]
