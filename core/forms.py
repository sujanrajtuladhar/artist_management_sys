from django import forms

from .constants import GENDER_CHOICES, ROLE_TYPE_CHOICES


class UserForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15, required=False)
    dob = forms.DateField(required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    address = forms.CharField(widget=forms.Textarea, required=False)
    role_type = forms.ChoiceField(choices=ROLE_TYPE_CHOICES)

    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")