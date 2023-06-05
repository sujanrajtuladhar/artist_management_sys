from django import forms

from .constants import GENDER_CHOICES, ROLE_TYPE_CHOICES
from .models import Artist, Music


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
        

class UserUpdateForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15, required=False)
    dob = forms.DateField(required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    address = forms.CharField(widget=forms.Textarea, required=False)
    role_type = forms.ChoiceField(choices=ROLE_TYPE_CHOICES)


class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['user', 'name', 'dob', 'gender', 'address', 'first_release_year', 'no_of_albums_released']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    

class ArtistUpdateForm(forms.Form):
    name = forms.CharField(max_length=255)
    dob = forms.DateField(required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    address = forms.CharField(widget=forms.Textarea, required=False)
    first_release_year = forms.DateField()
    no_of_albums_released = forms.IntegerField()
    

class ArtistImportForm(forms.Form):
    csv_file = forms.FileField(label='CSV File')


class MusicForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = ['title', 'album_name', 'genre']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'album_name': forms.TextInput(attrs={'class': 'form-control'}),
            'genre': forms.Select(attrs={'class': 'form-control'}),
        }