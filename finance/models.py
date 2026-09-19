from django.db import models
import random
import string
import calendar
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from datetime import date
from django.utils import timezone
from django.db.models import Q

from django.db.models.signals import post_save
from django.dispatch import receiver


from membership.models import Profile, User


# Generating Random Numbers for invoice 
def generate_invoice_number():
    # Generates a random alphanumeric string (e.g., INV-8F3K2)
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"INV-{random_part}"




class FeeSchedule(models.Model):
    base_fee = models.DecimalField(max_digits=15, decimal_places=2, default=5000)
    special_fee = models.DecimalField(max_digits=15, decimal_places=2, default=20000)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Regular Fee:{self.base_fee} | Special Fee: {self.special_fee}"
    

class PaymentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Cashier(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )


# Proparties Buy Sale Models
class Properties(models.Model):
    user = models.ManyToManyField(User, related_name="properties", limit_choices_to=~Q(user_type='Developer'))
    name = models.CharField(max_length=255, blank=False, null=False, default='Properties Name')
    details = models.TextField(blank=False, null=False, default='Properties Descriptions')
    document = models.ImageField(upload_to='payment_doc', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='properties_approved', limit_choices_to=~Q(user_type='Developer'))
    approved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



# Payment request models
class PaymentModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', limit_choices_to=~Q(user_type='Developer'))
    properties = models.ForeignKey(Properties, on_delete=models.CASCADE, blank=True, null=True, related_name='properties')
    invoice_number = models.CharField(max_length=20, unique=True, default=generate_invoice_number, editable=False)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, default='Select Purpose')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, default='Select Method')
    amount_of_money = models.DecimalField(max_digits=11, decimal_places=2, default='0.00')
    from_number = models.CharField(max_length=20, blank=True, null=True)
    pin_ref = models.CharField(max_length=20, blank=True, null=True)
    pay_year = models.IntegerField()
    pay_month = models.IntegerField()
    cashier = models.ForeignKey(Cashier, on_delete=models.CASCADE, default='Select Cashier')
    payment_note = models.CharField(max_length=500, blank=True, null=True)
    is_accept = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='approved_by', limit_choices_to=~Q(user_type='Developer'))
    approved_at = models.DateField(blank=True, null=True)
    document = models.ImageField(upload_to='payment_doc', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('invoice_number',) # Prevents duplicate payments for the same month

    def __str__(self):
        return f"{self.user.email} has submited payent for {self.pay_year}/{self.pay_month}"




class DuePayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='due_payment', limit_choices_to=~Q(user_type='Developer'))
    due_amount = models.DecimalField(max_digits=11, decimal_places=2, default='0.00')
    total_due_amount = models.DecimalField(max_digits=11, decimal_places=2, default='0.00')
    pay_year = models.IntegerField()
    pay_month = models.IntegerField()
    penalty_fee = models.DecimalField(max_digits=11, decimal_places=2, default='0.00')
    is_penalty = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate total_due_amount as the sum of due_amount and penalty_fee
        self.total_due_amount = Decimal(self.due_amount) + Decimal(self.penalty_fee)
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Created due payment record for {self.user.email}"



 
class PaymentSummery(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='payment_summery', limit_choices_to=~Q(user_type='Developer'))
    total_due_amount = models.DecimalField(max_digits=20, decimal_places=2, default='0.00')
    total_penalty_amount = models.DecimalField(max_digits=20, decimal_places=2, default='0.00')
    total_paid_amount = models.DecimalField(max_digits=20, decimal_places=2, default='0.00')
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Created payment summery record for {self.user.email}"








