from django.urls import path
from membership import views


app_name = 'membership'
urlpatterns = [
    path('membership/registration/', views.user_registration, name='user_register'),
    path('membership/login/', views.user_login, name='user_login'),
    path('membership/logout/', views.user_logout, name='user_logout'),

    path('', views.profile_view, name='profile_view'),
    path('membership/summary-view/', views.summary_view, name='summary_view'),
    path('membership/to-update-profile/', views.notice_to_update_profile, name='notice_to_update_profile'),
    path('membership/profile/update/<int:id>/', views.update_profile, name='update_profile'),
    path('membership/profile/sendMessage/', views.contact_us, name='contact_us'),

    # privacy page
    path('systems/privacy/terms-and-condition/', views.terms_and_condition_page, name='terms_and_condition'),
]
