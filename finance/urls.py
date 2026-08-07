from django.urls import path
from finance import views

app_name = 'finance'
urlpatterns = [
    path('transaction-list/', views.transaction_list, name='transaction_list'),
    path('payment-request/', views.payment_request, name='payment_request'),
    path('payment-request/<int:id>/<str:status>/', views.approve_or_reject_payment_request, name='approve_or_reject_payment_request'),
    path('payments/invoice-preview/<int:pk>/', views.invoice_preview, name='invoice_preview'),
    path('payments/invoice/download/<int:pk>/', views.invoice_download, name='invoice_download'),
]
