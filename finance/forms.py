from django.forms import ModelForm
from django import forms


from finance.models import PaymentRequestModel


class PaymentRequestForm(ModelForm):
    class Meta:
        model = PaymentRequestModel
        fields = ['calculation_type', 'payment_method', 'amount_of_money', 'from_number', 'pin_ref', 'cashier', 'payment_note']
        exclude = ('user', 'invoice_number')
        widgets = {
            'calculation_type': forms.Select(attrs={'class': 'form-control mb-4', 'id': 'validationCustom01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control mb-4', 'id': 'profession'}),
            'amount_of_money': forms.NumberInput(attrs={'class': 'form-control mb-4', 'id': 'profession'}),
            'from_number': forms.TextInput(attrs={'placeholder': '01800000000', 'class': 'form-control mb-4', 'id': 'profession'}),
            'pin_ref': forms.TextInput(attrs={'placeholder': 'Pin Number Or Referance', 'class': 'form-control mb-4', 'id': 'profession'}),
            'cashier': forms.Select(attrs={'placeholder': 'Refer To Cashier', 'class': 'form-control mb-4', 'id': 'profession'}),
            'payment_note': forms.TextInput(attrs={'placeholder': 'Write something..!', 'class': 'form-control mb-4', 'id': 'profession'})
            
        }


class PaymentViaAdminForm(ModelForm):
    class Meta:
        model = PaymentRequestModel
        fields = ['user', 'cashier', 'calculation_type', 'payment_method', 'amount_of_money', 'from_number', 'pin_ref', 'pay_month', 'payment_note']
        exclude = ('invoice_number',)
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control mb-4', 'id': 'validationCustom01'}),
            'cashier': forms.Select(attrs={'class': 'form-control mb-4', 'id': 'validationCustom01'}),
            'calculation_type': forms.Select(attrs={'class': 'form-control mb-4', 'id': 'validationCustom01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control mb-4', 'id': 'profession'}),
            'amount_of_money': forms.NumberInput(attrs={'class': 'form-control mb-4', 'id': 'profession'}),
            'from_number': forms.TextInput(attrs={'placeholder': '01800000000', 'class': 'form-control mb-4', 'id': 'profession'}),
            'pin_ref': forms.TextInput(attrs={'placeholder': 'Pin Number Or Referance', 'class': 'form-control mb-4', 'id': 'profession'}),
            'pay_month': forms.DateInput(attrs={'type': 'date', 'class': 'form-control mb-4', 'id': 'profession'}),
            'payment_note': forms.TextInput(attrs={'placeholder': 'Write something..!', 'class': 'form-control mb-4', 'id': 'profession'})
            
        }







