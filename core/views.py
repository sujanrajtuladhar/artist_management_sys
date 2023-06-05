from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db import connection
from django.shortcuts import render, redirect

from .forms import UserForm

# Create your views here.


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('core:dashboard')
        else:
            error_message = 'Invalid email or password'
    else:
        error_message = None

    return render(request, 'user/login.html', {'error_message': error_message})


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


def logout_user(request):
    logout(request)
    return redirect('core:login')


def register_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            dob = form.cleaned_data['dob']
            gender = form.cleaned_data['gender']
            address = form.cleaned_data['address']
            role_type = form.cleaned_data['role_type']
            password = make_password(form.cleaned_data['password'])
            is_staff = False  # Set the desired value
            is_superuser = False  # Set the desired value

            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO user (first_name, last_name, email, phone, dob, gender, address, role_type, "
                    "password, is_staff, is_superuser) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    [first_name, last_name, email, phone, dob, gender, address, role_type, password, is_staff, is_superuser]
                )

            return redirect('core:login')
    else:
        form = UserForm()

    return render(request, 'user/create_user.html', {'form': form})