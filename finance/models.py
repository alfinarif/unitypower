from django.db import models
import random
import string
from datetime import date
from django.utils import timezone
from django.db.models import Q

from simple_history.models import HistoricalRecords

from membership.models import User


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



# Proparties Buy Sale Models
class PropertiesBuySale(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    user = models.ManyToManyField(
        User, 
        related_name="properties",
        limit_choices_to=~Q(user_type='Developer')
        )
    name = models.CharField(max_length=255, blank=False, null=False, default='Properties Name')
    details = models.TextField(blank=False, null=False, default='Properties Descriptions')
    document = models.ImageField(upload_to='payment_doc', blank=True, null=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Pending')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='properties_approved')
    approved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name



# Payment request models
class PaymentRequestModel(models.Model):
    CALCULATION_TYPE = (
        ('Select Purpose', 'Select Purpose'),
        ('Savings', 'Savings'),
        ('Expense', 'Expense'),
        ('Loan', 'Loan'),
        ('Welfare', 'Welfare')

    )
    PAYMENT_METHOD = (
        ('Select Method', 'Select Method'),
        ('Developments', 'Developments'),
        ('Bkash', 'Bkash'),
        ('Rocket', 'Rocket'),
        ('Cash', 'Cash'),
        ('Bank', 'Bank'),
    )

    CASHIER_LIST = (
        ('Select Cashier', 'Select Cashier'),
        ('Borhan-Uddin', 'Boran-Uddin'),
        ('Foysal-Ahammed', 'Foysal-Ahammed')
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='payment_request',
        limit_choices_to=~Q(user_type='Developer')
        )
    properties = models.ForeignKey(PropertiesBuySale, on_delete=models.CASCADE, blank=True, null=True, related_name='properties')
    invoice_number = models.CharField(max_length=20, unique=True, default=generate_invoice_number, editable=False)
    calculation_type = models.CharField(max_length=100, choices=CALCULATION_TYPE, default='Select Purpose')
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD, default='Select Method')
    amount_of_money = models.DecimalField(max_digits=11, decimal_places=2, default='0.00')
    from_number = models.CharField(max_length=20, blank=True, null=True)
    pin_ref = models.CharField(max_length=20, blank=True, null=True)
    pay_year = models.IntegerField()
    pay_month = models.IntegerField()
    cashier = models.CharField(max_length=100, choices=CASHIER_LIST, default='Select Cashier')
    payment_note = models.CharField(max_length=500, blank=True, null=True)
    is_accept = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Pending')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='approved_by')
    approved_at = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    document = models.ImageField(upload_to='payment_doc', blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('user', 'pay_year', 'pay_month') # Prevents duplicate payments for the same month

    def __str__(self):
        return f"{self.user.email} has submited payent for {self.pay_year}/{self.pay_month}"




    








