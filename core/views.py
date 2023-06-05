from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

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