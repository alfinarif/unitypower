from django.forms import ModelForm
from django import forms

import calendar
from django.utils import timezone

from finance.models import PaymentRequestModel


class PaymentRequestForm(ModelForm):

    class Meta:
        # Tuple format: (Integer_Value_For_DB, String_Label_For_UI)
        YEAR_CHOICES = [(y, str(y)) for y in range(2024, 2031)]
        # Generates: [(1, 'January'), (2, 'February'), ..., (12, 'December')]
        MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]

        model = PaymentRequestModel
        fields = ['calculation_type', 'payment_method', 'amount_of_money', 'from_number', 'pay_year', 'pay_month', 'pin_ref', 'cashier', 'payment_note']
        exclude = ('user', 'invoice_number')
        
        widgets = {
            'calculation_type': forms.Select(attrs={'class': 'form-control mb-4', 'id': 'validationCustom01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control mb-4', 'id': 'profession'}),
            'amount_of_money': forms.NumberInput(attrs={'class': 'form-control mb-4', 'id': 'profession'}),
            'from_number': forms.TextInput(attrs={'placeholder': '01800000000', 'class': 'form-control mb-4', 'id': 'profession'}),

            'pay_year': forms.Select(choices=YEAR_CHOICES, attrs={'class': 'form-control mb-4', 'id': 'profession'}),
            'pay_month': forms.Select(choices=MONTH_CHOICES, attrs={'class': 'form-control mb-4', 'id': 'profession'}),

            'pin_ref': forms.TextInput(attrs={'placeholder': 'Pin Number Or Referance', 'class': 'form-control mb-4', 'id': 'profession'}),
            'cashier': forms.Select(attrs={'placeholder': 'Refer To Cashier', 'class': 'form-control mb-4', 'id': 'profession'}),
            'payment_note': forms.TextInput(attrs={'placeholder': 'Write something..!', 'class': 'form-control mb-4', 'id': 'profession'})
            
        }

    # 3. Use __init__ to set dynamic dynamic initial values (Current Month & Year)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Automatically defaults dropdowns to current live date upon page load
        self.fields['pay_year'].initial = timezone.now().year
        self.fields['pay_month'].initial = timezone.now().month


class PaymentViaAdminForm(ModelForm):
    class Meta:
        # Tuple format: (Integer_Value_For_DB, String_Label_For_UI)
        YEAR_CHOICES = [(y, str(y)) for y in range(2024, 2031)]
        # Generates: [(1, 'January'), (2, 'February'), ..., (12, 'December')]
        MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]

        model = PaymentRequestModel
        fields = ['user', 'cashier', 'calculation_type', 'payment_method', 'amount_of_money', 'from_number', 'pay_year', 'pay_month', 'pin_ref', 'pay_month', 'payment_note']
        exclude = ('invoice_number',)
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control mb-4', 'id': 'validationCustom01'}),
            'cashier': forms.Select(attrs={'class': 'form-control mb-4', 'id': 'validationCustom01'}),
            'calculation_type': forms.Select(attrs={'class': 'form-control mb-4', 'id': 'validationCustom01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control mb-4', 'id': 'profession'}),
            'amount_of_money': forms.NumberInput(attrs={'class': 'form-control mb-4', 'id': 'profession'}),
            'from_number': forms.TextInput(attrs={'placeholder': '01800000000', 'class': 'form-control mb-4', 'id': 'profession'}),

            'pay_year': forms.Select(choices=YEAR_CHOICES, attrs={'class': 'form-control mb-4', 'id': 'profession'}),
            'pay_month': forms.Select(choices=MONTH_CHOICES, attrs={'class': 'form-control mb-4', 'id': 'profession'}),

            'pin_ref': forms.TextInput(attrs={'placeholder': 'Pin Number Or Referance', 'class': 'form-control mb-4', 'id': 'profession'}),
            'payment_note': forms.TextInput(attrs={'placeholder': 'Write something..!', 'class': 'form-control mb-4', 'id': 'profession'})
            
        }

    # 3. Use __init__ to set dynamic dynamic initial values (Current Month & Year)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Automatically defaults dropdowns to current live date upon page load
        self.fields['pay_year'].initial = timezone.now().year
        self.fields['pay_month'].initial = timezone.now().month







