from django.db import models
from datetime import date

from django.contrib.auth.models import BaseUserManager, AbstractUser, PermissionsMixin

from django.dispatch import receiver
from django.db.models.signals import post_save

from simple_history.models import HistoricalRecords


# CUSTOM USER MANAGER
class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    # OVERRIDE CREATE_USER METHOD
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('User must have a email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # OVERRIDE CREATE_SUPERUSER METHOD 
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must be have is_staff True")

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must be have is_superuser True")

        if extra_fields.get('is_active') is not True:
            raise ValueError("Superuser must be have is_active True")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    USER_TYPE = (
        ('Member', 'Member'),
        ('Chief-Adviser', 'Chief-Adviser'),
        ('President', 'President'),
        ('Vice-President', 'Vice-President'),
        ('Chief-Cashier', 'Chief-Cashier'),
        ('Assistant-Cashier', 'Assistant-Cashier'),
        ('Organizing-Committee', 'Organizing-Committee'),
        ('Editor', 'Editor'),
        ('Developer', 'Developer'),
        ('Hr', 'Hr'),
        ('Admin', 'Admin')
    )

    username = None
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=100, choices=USER_TYPE, default='Member')
    account_number = models.CharField(max_length=30, blank=True, null=True)
    is_hr = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_finance = models.BooleanField(default=False)
    history = HistoricalRecords()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()


class Profile(models.Model):
    RELIGION_TYPE = (
        ('Muslim', 'Muslim'),
        ('Hindu', 'Hindu')
    )
    GENDER_TYPE = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )
    MARITAL_STATUS = (
        ('Married', 'Married'),
        ('Unmarried', 'Unmarried')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100, blank=True, null=True)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    national_id = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    profession = models.CharField(max_length=255, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    upazila = models.CharField(max_length=100, blank=True, null=True)
    post_office = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    current_address = models.CharField(max_length=255, blank=True, null=True)
    religion = models.CharField(max_length=50, choices=RELIGION_TYPE, default='Muslim')
    gender = models.CharField(max_length=50, choices=GENDER_TYPE, default='Male')
    marital_status = models.CharField(max_length=50, choices=MARITAL_STATUS, default='Unmarried')
    blood_group = models.CharField(max_length=100, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatar', blank=True, null=True)
    created_date = models.DateField(auto_now_add=True, editable=True)
    updated_date = models.DateField(blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.user.email}'s Profile"

    @receiver(post_save, sender=User)
    def create_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_profile(sender, instance, **kwargs):
        current_profile = instance.profile
        current_profile.created_date = '2024-12-01'
        current_profile.save()

    @property
    def is_fully_filled(self):
        field_names = [f.name for f in self._meta.get_fields()]
        for field_name in field_names:
            value = getattr(self, field_name)
            if value is None or value == '':
                return False
        return True


class Nominee(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='nominee')
    full_name = models.CharField(max_length=100, blank=True, null=True)
    relation = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.profile.user.email}'s Nominee"

    @receiver(post_save, sender=Profile)
    def create_nominee(sender, instance, created, **kwargs):
        if created:
            Nominee.objects.create(profile=instance)

    @receiver(post_save, sender=Profile)
    def save_nominee(sender, instance, **kwargs):
        current_nominee = instance.nominee
        current_nominee.created_date = '2024-12-01'
        current_nominee.save()



class ContactUs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_us')
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    is_seen = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.user.email} Send A Message!"










