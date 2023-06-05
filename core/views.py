from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db import connection
from django.shortcuts import render, redirect

from functools import wraps

from .forms import UserForm, UserUpdateForm

# Create your views here.


def super_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role_type != 'super_admin':
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


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


@login_required
@super_admin_required
def user_list(request):
    # List the user records with pagination [Role Access: super_admin]
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 1))

    with connection.cursor() as cursor:
        offset = (page - 1) * limit
        cursor.execute("SELECT id, first_name, last_name, phone, address, gender, email, role_type FROM user LIMIT %s OFFSET %s", (limit, offset))
        # fetch all
        users = cursor.fetchall()
        # count total users
        cursor.execute("SELECT COUNT(*) FROM user")
        total_users = cursor.fetchone()[0]
        # calculate total pages
        total_pages = total_users / limit
        # calculate next page
        next_page = page + 1 if page < total_pages else None
        # calculate prev page
        prev_page = page - 1 if page > 1 else None
        # calculate page range
        page_range = range(1, int(total_pages) + 1)

    # paginate user with limit of 2 per page using cursor execute command
    users_list = []
    for user in users:
        user_dict = {
            'id': user[0],
            'first_name': user[1],
            'last_name': user[2],
            'phone': user[3],
            'address': user[4],
            'gender': user[5],
            'email': user[6],
            'role_type': user[7]
        }
        users_list.append(user_dict)
    # return the list of users with pagination details like page, limit, total_pages, next_page, prev_page
    context = {
        'users': users_list,
        'total_pages': int(total_pages),
        'page': page,
        'limit': limit,
        'next_page': int(next_page) if next_page else None,
        'prev_page': int(prev_page) if prev_page else None,
        'page_range': page_range,
    }

    return render(request, 'user/user_list.html', context)


@login_required
@super_admin_required
def create_user(request):
    # Create a new user record [Role Access: super_admin]

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

            is_staff, is_superuser = False, False  # Set the desired value
            if role_type == 'super_admin':
                is_staff, is_superuser = True, True

            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO user (first_name, last_name, email, phone, dob, gender, address, role_type, "
                    "password, is_staff, is_superuser) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    [first_name, last_name, email, phone, dob, gender, address, role_type, password, is_staff, is_superuser]
                )

            return redirect('core:user_list')
    else:
        form = UserForm()

    return render(request, 'user/create_user.html', {'form': form})


@login_required
@super_admin_required
def update_user(request, user_id):
    # Update an existing user record [Role Access: super_admin]

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, first_name, last_name, email, phone, dob, gender, address, role_type FROM user WHERE id = %s", [user_id])
        user = cursor.fetchone()

    if not user:
        return redirect('core:user_list')

    if request.method == 'POST':
        form = UserUpdateForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            dob = form.cleaned_data['dob']
            gender = form.cleaned_data['gender']
            address = form.cleaned_data['address']
            role_type = form.cleaned_data['role_type']

            with connection.cursor() as cursor:
                cursor.execute("UPDATE user SET first_name = %s, last_name = %s, email = %s, phone = %s, dob = %s, gender = %s, address = %s, role_type = %s WHERE id = %s", [first_name, last_name, email, phone, dob, gender, address, role_type, user_id])

            return redirect('core:user_list')
    else:
        form = UserUpdateForm(initial={
            'first_name': user[1],
            'last_name': user[2],
            'email': user[3],
            'phone': user[4],
            'dob': user[5],
            'gender': user[6],
            'address': user[7],
            'role_type': user[8]
        })

    return render(request, 'user/update_user.html', {'form': form, 'user': user})


@login_required
@super_admin_required
def delete_user(request, user_id):
    # Delete a user record [Role Access: super_admin]

    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM user WHERE id = %s", [user_id])
        user = cursor.fetchone()

    if not user:
        return redirect('core:user_list')

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM user WHERE id = %s", [user_id])

    return redirect('core:user_list')