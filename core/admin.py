from django.contrib import admin
from .models import User, Artist, Music

# Register your models here.
admin.site.register([User, Artist, Music])