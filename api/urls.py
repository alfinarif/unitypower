
from django.urls import include, path

from . import views


urlpatterns = [
    path("register/", views.RegistrationViewSet.as_view({"post": "create"}), name="register"),
    path("login/", views.LoginViewSet.as_view({"post": "create"}), name="login"),
    path("profile/update/<int:pk>/", views.UpdateProfileViewSet.as_view({"get": "retrieve", "put": "update"}), name="profile_update"),
    path("contact-us/", views.ContactUsViewSet.as_view({"post": "create", "get": "list"}), name="contact_us"),
    path("contact-us/<int:pk>/", views.ContactUsViewSet.as_view({"get": "retrieve"}), name="contact_us_detail"),
    path("payment-summery/", views.PaymentSummeryViewSet.as_view({"get": "list"}), name="payment_summery"),
]
