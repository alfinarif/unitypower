from django.forms import ModelForm
from django import forms

from administration.models import WhatsappNotificationModel


class WhatsappNotificationToPerUserForm(ModelForm):
    class Meta:
        model = WhatsappNotificationModel
        fields = ['users', 'company', 'message']
        widgets = {
            'users': forms.Select(attrs={'class': 'form-control mb-4 d-flex width=100 mb-4 mail-form', 'id': 'validationCustom01'}),
            'company': forms.TextInput(attrs={'class': 'form-control mb-4 ', 'placeholder': 'Company Name Or Department', 'id': 'm-subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control mb-4', 'rows': '6', 'placeholder': 'Write Messages To Send', 'id': 'm-subject'}),
        }


class WhatsappNotificationForm(ModelForm):
    class Meta:
        model = WhatsappNotificationModel
        fields = ['company', 'message']
        exclude = ('users',)
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control mb-4 ', 'placeholder': 'Company Name Or Department', 'id': 'm-subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control mb-4', 'rows': '6', 'placeholder': 'Write Messages To Send', 'id': 'm-subject'}),
        }



