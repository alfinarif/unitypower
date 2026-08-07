from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm

from membership.models import User, Profile, Nominee, ContactUs


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'account_number', 'password1', 'password2']

        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control', 'id': 'email', 'name': 'email', 'type': 'text', 'placeholder': 'Example@gmail.com'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'id': 'email', 'name': 'email', 'type': 'text', 'placeholder': 'ID Number'}),
            'password1': forms.TextInput(attrs={'class': 'form-control', 'id': 'password', 'name': 'password', 'type': 'password', 'placeholder': 'Password'}),
            'password2': forms.TextInput(attrs={'class': 'form-control', 'id': 'password', 'name': 'password', 'type': 'password', 'placeholder': 'Confirm Password'}),
        }


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ['email','account_number', 'user_type', 'is_hr', 'is_admin', 'is_finance']

        widgets = {
            'email': forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control mb-4', 'id': 'profession'}),
            'account_number': forms.TextInput(attrs={'placeholder': 'ID Number', 'class': 'form-control mb-4', 'id': 'profession'}),
            'user_type': forms.Select(attrs={'placeholder': 'Religion', 'class': 'form-control mb-4', 'id': 'profession'}),
            'is_hr': forms.CheckboxInput(attrs={'placeholder': 'Religion', 'class': 'form-control mb-4', 'id': 'profession'}),
            'is_admin': forms.CheckboxInput(attrs={'placeholder': 'Religion', 'class': 'form-control mb-4', 'id': 'profession'}),
            'is_finance': forms.CheckboxInput(attrs={'placeholder': 'Religion', 'class': 'form-control mb-4', 'id': 'profession'}),
            
        }





class ProfileInfoForm(ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ('user', 'updated_date')
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control mb-4', 'id': 'profession'}),
            'father_name': forms.TextInput(attrs={'placeholder': 'Father Name', 'class': 'form-control mb-4', 'id': 'profession'}),
            'mother_name': forms.TextInput(attrs={'placeholder': 'Mother Name', 'class': 'form-control mb-4', 'id': 'profession'}),
            'national_id': forms.TextInput(attrs={'placeholder': 'National Id', 'class': 'form-control mb-4', 'id': 'profession'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'form-control mb-4', 'id': 'profession'}),
            'profession': forms.TextInput(attrs={'placeholder': 'Profession', 'class': 'form-control mb-4', 'id': 'profession'}),
            'district': forms.TextInput(attrs={'placeholder': 'District', 'class': 'form-control mb-4', 'id': 'profession'}),
            'upazila': forms.TextInput(attrs={'placeholder': 'Upazila', 'class': 'form-control mb-4', 'id': 'profession'}),
            'post_office': forms.TextInput(attrs={'placeholder': 'Post Office', 'class': 'form-control mb-4', 'id': 'profession'}),
            'village': forms.TextInput(attrs={'placeholder': 'Village', 'class': 'form-control mb-4', 'id': 'profession'}),
            'current_address': forms.TextInput(attrs={'placeholder': 'Current Address', 'class': 'form-control mb-4', 'id': 'profession'}),
            'religion': forms.Select(attrs={'placeholder': 'Religion', 'class': 'form-control mb-4', 'id': 'profession'}),
            'gender': forms.Select(attrs={'class': 'form-control mb-4', 'id': 'profession'}),
            'marital_status': forms.Select(attrs={'class': 'form-control mb-4', 'id': 'profession'}),
            'blood_group': forms.TextInput(attrs={'placeholder': 'Blood Group', 'class': 'form-control mb-4', 'id': 'profession'}),
            'birthday': forms.DateInput(attrs={'placeholder': 'MM-DD-YYYY', 'type': 'date', 'class': 'form-control mb-4', 'id': 'profession'}),
            'avatar': forms.TextInput(attrs={'class': 'dropify', 'id': 'input-file-max-fs', 'type': 'file'}),

        }


class NomineeInfoForm(ModelForm):
    class Meta:
        model = Nominee
        fields = '__all__'
        exclude = ('profile',)


class ContactUsForm(ModelForm):
    class Meta:
        model = ContactUs
        fields = ['subject', 'message']
        exclude = ('user',)

        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'email', 
                'name': 'email', 
                'type': 'text', 
                'placeholder': 'Write your subject..!'
                }),
            'message': forms.Textarea(attrs={
                'rows': 8,
                'aria-label': 'With textarea',
                'class': 'form-control', 
                'placeholder': 'Write your messages...!'
            }),
        }