from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='user_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
]