from django.contrib.auth import authenticate, get_user_model
from django.forms.models import model_to_dict
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from membership.models import User, Profile, Nominee, ContactUs
from finance.models import PaymentSummery



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            email=attrs["email"],
            password=attrs["password"],
        )
        if user is None:
            raise AuthenticationFailed("Invalid email or password.")

        attrs["user"] = user
        return attrs



class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("email", "password", "password_confirm")

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class NomineeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nominee
        
        fields = [
            "profile",
            "full_name",
            "relation",
            "address",
            "phone_number",
            "created_date",
            "updated_date"
        ]



class ProfileSerializer(serializers.ModelSerializer):
    nominee = NomineeSerializer(read_only=True)
    class Meta:
        model = Profile
        # Include avatar and any other profile fields
        fields = [
            "user",
            "full_name",
            "father_name",
            "mother_name",
            "national_id",
            "phone_number",
            "profession",
            "district",
            "upazila",
            "post_office",
            "village",
            "current_address",
            "religion",
            "gender",
            "marital_status",
            "blood_group",
            "birthday",
            "avatar",
            "created_date",
            "updated_date",
            "nominee"
        ] 
        extra_kwargs = {
            # Bypasses the ValueError if the user has no avatar uploaded yet
            'avatar': {'allow_null': True, 'required': False} 
        }


class UpdateProfileSerializer(ProfileSerializer):
    """Serializer for updating profile fields and the related nominee."""
    nominee = NomineeSerializer(required=False)

    def update(self, instance, validated_data):
        nominee_data = validated_data.pop("nominee", None)
        instance = super().update(instance, validated_data)

        if nominee_data is not None:
            try:
                nominee = instance.nominee
            except Nominee.DoesNotExist:
                profile_field = next(
                    (
                        field
                        for field in Nominee._meta.get_fields()
                        if field.concrete
                        and field.is_relation
                        and field.remote_field.model is Profile
                    ),
                    None,
                )
                if profile_field is None:
                    raise serializers.ValidationError(
                        {"nominee": "A nominee cannot be created for this profile."}
                    )
                nominee_data[profile_field.name] = instance
                nominee = Nominee.objects.create(**nominee_data)
            else:
                for field, value in nominee_data.items():
                    setattr(nominee, field, value)
                nominee.save()

        return instance


class ContactUsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ContactUs
        fields = ("id", "user", "subject", "message", "is_seen", "created")
        read_only_fields = ("id", "user", "is_seen", "created")

    def create(self, validated_data):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError({"user": "An authenticated user is required."})
        return ContactUs.objects.create(user=request.user, **validated_data)


class PaymentSummerySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSummery
        fields = (
            "id",
            "user",
            "total_due_amount",
            "total_penalty_amount",
            "total_paid_amount",
            "credit_amount",
            "is_active",
            "created",
        )
        read_only_fields = ("id", "created")


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    payment_summery = PaymentSummerySerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "user_type", "account_number", "is_hr", "is_admin", "is_finance", "profile", "payment_summery")
        read_only_fields = fields




