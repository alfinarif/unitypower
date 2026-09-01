from django.urls import path
from administration import views


app_name = 'administration'
urlpatterns = [
    # admin paths
    path('index/', views.admin_index_view, name='admin_index'),
    path('user-list/', views.admin_user_list_view, name='admin_user_list'),
    path('user-list/update/<int:id>/', views.admin_user_update_view, name='admin_user_update'),
    path('profile-list/', views.admin_profile_list_view, name='admin_profile_list'),
    path('transactions-list/', views.admin_transaction_list, name='admin_transaction_list'),
    path('properties-list/', views.admin_properties_list_view, name='admin_properties_list_view'),
    path('unpaid-reports-list/', views.admin_unpaid_report_list, name='admin_unpaid_report_list'),
    path('nominee-list/', views.admin_nominee_list_view, name='admin_nominee_list'),
    path('nominee-list/update/<int:id>/', views.admin_nominee_update_view, name='admin_nominee_update'),
    path('messages-list/', views.admin_message_list_view, name='admin_message_list'),
    path('notification-list/', views.admin_notification_view, name='admin_notification_view'),

    # whatsapp notification endpoint
    path('send-notification/<int:id>/', views.send_whatsapp_notification_to_unpaid_user, name='send_whatsapp_notification_to_unpaid_user'),

    # export/download data
    path('data/trans/export/<str:format>/', views.export_all_transactions_data, name='export_all_transactions_data'),
    path('data/members/export/<str:format>/', views.export_user_access_data, name='export_user_access_data'),
    path('transaction/invoice/export/<int:pk>/', views.export_all_invoice_data, name='export_invoice_data'),
    # download reports as pdf
    path('data/members/export-report/pdf/', views.download_member_report_view, name='download_member_report_pdf'),
    path('data/members/profile/export-report/pdf/', views.download_profile_report_view, name='download_profile_report_pdf'),
    path('data/members/profile/nominee/export-report/pdf/', views.download_nominee_report_view, name='download_nominee_report_pdf'),
    path('data/finance/transactions/list/export-report/pdf/', views.download_transaction_report_view, name='download_transaction_report_pdf'),

]
