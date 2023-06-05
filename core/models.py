from django.contrib.auth.models import (
    AbstractBaseUser, 
    PermissionsMixin)
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import (
    GENDER_CHOICES, 
    GENRE_CHOICES, 
    ROLE_TYPE_CHOICES)
from .managers import UserManager

# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(
        max_length=50, help_text=_('Enter the first name'))
    last_name = models.CharField(
        max_length=50, null=True, blank=True, help_text=_('Enter the last name'))
    email = models.EmailField(
        unique=True, help_text=_('Enter the email address'))
    phone = models.CharField(
        max_length=15, null=True, blank=True, help_text=_('Enter the phone number'))
    dob = models.DateField(
        null=True, blank=True, help_text=_('Enter the date of birth'))
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, help_text=_('Select the gender'))
    address = models.TextField(
        null=True, blank=True, help_text=_('Enter the address'))
    role_type = models.CharField(
        max_length=14, choices=ROLE_TYPE_CHOICES, help_text=_('Select the role type'))

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    # Specify the email field as the username field
    USERNAME_FIELD = 'email'
    # Add the required fields for the create_user() method
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'dob', 'gender', 'address', 'role_type']

    # # Add the is_staff and is_superuser fields
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    class Meta:
        db_table = 'user'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email
    

class Artist(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, help_text='User associated with the artist')

    name = models.CharField(
        max_length=255, help_text=_('Artist name'))
    dob = models.DateField(
        null=True, blank=True, 
        help_text=_('Date of birth'))
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, 
        help_text=_('Gender'))
    address = models.TextField(
        null=True, blank=True, 
        help_text=_('Artist address'))
    first_release_year = models.DateField(
        help_text=_('First release year'))
    no_of_albums_released = models.PositiveIntegerField(
        help_text=_('Number of albums released'))
    created_at = models.DateTimeField(
        auto_now_add=True, null=True, 
        help_text=_('Creation timestamp'))
    updated_at = models.DateTimeField(
        auto_now=True, null=True, 
        help_text=_('Last update timestamp'))

    def __str__(self) -> str:
        return self.name


class Music(models.Model):
    artist_relation = models.ForeignKey(
        Artist, 
        related_name='music', 
        on_delete=models.CASCADE
        help_text=_('Artist associated with the music'))
    title = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    genre = models.CharField(max_length=7, choices=GENRE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True, null=True)

    def __str__(self) -> str:
        return self.title