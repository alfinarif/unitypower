from django.contrib.auth import login
from rest_framework import mixins, status, viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from membership.models import ContactUs, Profile
from finance.models import PaymentSummery
from .serializers import (
    RegistrationSerializer, 
    LoginSerializer, 
    UserSerializer, 
    UpdateProfileSerializer,
    ContactUsSerializer,
    PaymentSummerySerializer
    )




class RegistrationViewSet(viewsets.GenericViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {"user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginViewSet(viewsets.GenericViewSet):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        login(request, user)

        return Response(
            {"user": UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )


class UpdateProfileViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet,):
    """Retrieve or update the authenticated user's profile."""

    serializer_class = UpdateProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        # If the user is staff/admin, let them see and update all profiles
        if user.is_hr or user.is_admin or user.is_finance:
            return Profile.objects.all()
        # Regular users can only access their own profile
        return Profile.objects.filter(user=user)


class ContactUsViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Authenticated users can submit (create) contact messages.
    Admin, HR, and Finance roles can view lists and details of all messages.
    """
    serializer_class = ContactUsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Optimize database query by pre-joining the user model
        queryset = ContactUs.objects.select_related("user").order_by("-created")
        user = self.request.user
        
        # Check for administrative roles
        if getattr(user, 'is_admin', False) or getattr(user, 'is_hr', False) or getattr(user, 'is_finance', False) or user.is_staff:
            return queryset
            
        # If standard users should see ONLY their own records in lists/retrievals:
        return queryset.filter(user=user)

    def list(self, request, *args, **kwargs):
        # Optional Safeguard: If regular users shouldn't even be allowed to call the LIST endpoint, block them entirely
        user = request.user
        is_privileged = getattr(user, 'is_admin', False) or getattr(user, 'is_hr', False) or getattr(user, 'is_finance', False) or user.is_staff
        if not is_privileged:
            raise PermissionDenied("You do not have permission to view contact inquiries.")
        return super().list(request, *args, **kwargs)


class PaymentSummeryViewSet(viewsets.ModelViewSet):
    """Create, list, retrieve, update, and delete payment summaries."""

    queryset = PaymentSummery.objects.select_related("user").all()
    serializer_class = PaymentSummerySerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        # Payment summaries contain financial data; only finance/admin staff
        # may access them, while authentication is required for every action.
        return [PaymentSummaryStaffPermission()]


class PaymentSummaryStaffPermission(permissions.BasePermission):
    """Allow payment-summary access to finance, admin, or staff accounts."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                getattr(user, "is_admin", False)
                or getattr(user, "is_finance", False)
                or user.is_hr
            )
        )


















