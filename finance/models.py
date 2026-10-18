import os

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
        ('PENDING_ASSISTANT_CASHIER', 'Pending Assistant Cashier Approval'),
        ('PENDING_CHIEF_CASHIER', 'Pending Chief Cashier Approval'),
        ('PENDING_VICE_PRESIDENT', 'Pending Vice President Approval'),
        ('PENDING_PRESIDENT', 'Pending President Approval'),
    )


# Proparties Buy Sale Models
class Properties(models.Model):
    user = models.ManyToManyField(User, related_name="properties", limit_choices_to=~Q(user_type='Developer'))
    name = models.CharField(max_length=255, blank=False, null=False, default='Properties Name')
    amount = models.DecimalField(max_digits=50, decimal_places=2, default='0.00')
    details = models.TextField(blank=False, null=False, default='Properties Descriptions')
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='PENDING_ASSISTANT_CASHIER')

    assistant_cashier_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assistant_cashier_approvals')
    chief_cashier_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chief_cashier_approvals')
    vice_president_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='vice_president_approvals')
    president_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='president_approvals')

    assistant_cashier_at = models.DateTimeField(null=True, blank=True)
    chief_cashier_at = models.DateTimeField(null=True, blank=True)
    vice_president_at = models.DateTimeField(null=True, blank=True)
    president_at = models.DateTimeField(null=True, blank=True)

    approved_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    @property
    def filename(self):
        # Extracts just the last part of the path (the actual file name)
        return os.path.basename(self.document.name)

    def approve(self, user):
        """Advances the state machine sequentially based on user role."""
        if self.status == 'PENDING_ASSISTANT_CASHIER' and user.user_type == 'Assistant-Cashier':
            self.status = 'PENDING_CHIEF_CASHIER'
            self.assistant_cashier_by = user
            self.assistant_cashier_at = timezone.now()
        elif self.status == 'PENDING_CHIEF_CASHIER' and user.user_type == 'Chief-Cashier':
            self.status = 'PENDING_VICE_PRESIDENT'
            self.chief_cashier_by = user
            self.chief_cashier_at = timezone.now()
        elif self.status == 'PENDING_VICE_PRESIDENT' and user.user_type == 'Vice-President':
            self.status = 'PENDING_PRESIDENT'
            self.vice_president_by = user
            self.vice_president_at = timezone.now()
        elif self.status == 'PENDING_PRESIDENT' and user.user_type == 'President':
            self.status = 'Approved'
            self.president_by = user
            self.president_at = timezone.now()
        else:
            pass  # Invalid role for the current status; do nothing
        
        self.save()

    def reject(self, user):
        """Any authorized stage role can reject the workflow."""
        valid_roles = {
            'PENDING_ASSISTANT_CASHIER': 'Assistant-Cashier',
            'PENDING_CHIEF_CASHIER': 'Chief-Cashier',
            'PENDING_VICE_PRESIDENT': 'Vice-President',
            'PENDING_PRESIDENT': 'President'
        }
        
        required_group = valid_roles.get(self.status)
        if required_group and user.user_type == required_group:
            self.status = 'Rejected'
            self.save()
        else:
            pass
    
    def get_step_progress(self):
        """Returns structural info about the stages to be rendered in templates."""
        stages = [
            {'code': 'PENDING_ASSISTANT_CASHIER', 'label': f'Assistant Cashier {self.assistant_cashier_by} Review', 'date': self.assistant_cashier_at, 'approved_by': self.assistant_cashier_by},
            {'code': 'PENDING_CHIEF_CASHIER', 'label': f'Chief Cashier {self.chief_cashier_by} Review', 'date': self.chief_cashier_at, 'approved_by': self.chief_cashier_by},
            {'code': 'PENDING_VICE_PRESIDENT', 'label': f'Vice President {self.vice_president_by} Review', 'date': self.vice_president_at, 'approved_by': self.vice_president_by },
            {'code': 'PENDING_PRESIDENT', 'label': f'President {self.president_by} Review', 'date': self.president_at, 'approved_by': self.president_by},
        ]
        
        # Determine the active numerical index
        status_indices = {
            'PENDING_ASSISTANT_CASHIER': 0,
            'PENDING_CHIEF_CASHIER': 1,
            'PENDING_VICE_PRESIDENT': 2,
            'PENDING_PRESIDENT': 3,
            'Rejected': -1, # Special case for rejected

        }
        
        current_index = status_indices.get(self.status, 0)
        
        steps = []
        for i, stage in enumerate(stages):
            if self.status == 'Rejected':
                status_class = 'text-danger' if i == current_index else 'text-warning'
            elif i < current_index:
                status_class = 'text-success'
            elif i == current_index:
                status_class = 'text-primary'
            else:
                status_class = 'text-ligh'
                
            steps.append({
                'label': stage['label'],
                'date': stage['date'],
                'approved_by': stage['approved_by'],
                'class': status_class,
                'is_current': i == current_index
            })
            
        return steps

    

class PropertiesFile(models.Model):
    properties = models.ForeignKey(Properties, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='properties_doc/', blank=True, null=True)

    def __str__(self):
        return f"File for {self.properties.name}"


# Payment request models
class PaymentModel(models.Model):
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', limit_choices_to=~Q(user_type='Developer'))
    properties = models.ForeignKey(Properties, on_delete=models.CASCADE, blank=True, null=True, related_name='properties', limit_choices_to=Q(status='Approved'))
    invoice_number = models.CharField(max_length=20, unique=True, default=generate_invoice_number, editable=False)
    payment_type = models.CharField(max_length=100, choices=CALCULATION_TYPE, default='Select Purpose')
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD, default='Select Method')
    amount_of_money = models.DecimalField(max_digits=200, decimal_places=2, default='0.00')
    from_number = models.CharField(max_length=20, blank=True, null=True)
    pin_ref = models.CharField(max_length=20, blank=True, null=True)
    pay_year = models.IntegerField()
    pay_month = models.IntegerField()
    cashier = models.ForeignKey(Cashier, on_delete=models.CASCADE, blank=True, null=True)
    payment_note = models.CharField(max_length=500, blank=True, null=True)
    is_accept = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Pending')
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
    due_amount = models.DecimalField(max_digits=200, decimal_places=2, default='0.00')
    pay_year = models.IntegerField()
    pay_month = models.IntegerField()
    penalty_fee = models.DecimalField(max_digits=200, decimal_places=2, default='0.00')
    is_penalty = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Pending')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Created due payment record for {self.user.email}"



 
class PaymentSummery(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='payment_summery', limit_choices_to=~Q(user_type='Developer'))
    total_due_amount = models.DecimalField(max_digits=200, decimal_places=2, default='0.00')
    total_penalty_amount = models.DecimalField(max_digits=200, decimal_places=2, default='0.00')
    total_paid_amount = models.DecimalField(max_digits=200, decimal_places=2, default='0.00')
    credit_amount = models.DecimalField(max_digits=200, decimal_places=2, default='0.00')
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Created payment summery record for {self.user.email}"








