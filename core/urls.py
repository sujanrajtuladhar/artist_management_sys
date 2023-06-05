from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='user_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),

    # `User`
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/update/<int:user_id>/', views.update_user, name='update_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    # `Artist`
    path('artists/', views.artist_list, name='artist_list'),
    path('artists/create/', views.create_artist, name='create_artist'),
    path('artists/update/<int:artist_id>/', views.update_artist, name='update_artist'),
    path('artists/delete/<int:artist_id>/', views.delete_artist, name='delete_artist'),

    path('artists/import_csv/', views.import_artist_csv, name='import_artist_csv'),
    path('artists/export_csv/', views.export_artist_csv, name='export_artist_csv'),
    
    # `Music`
    path('artists/songs/<int:artist_id>/', views.song_list, name='song_list'),
    path('artists/songs/create/<int:artist_id>/', views.create_song, name='create_song'),
    path('artists/songs/update/<int:artist_id>/<int:song_id>/', views.update_song, name='update_song'),
    path('artists/songs/delete/<int:artist_id>/<int:song_id>/', views.delete_song, name='delete_song'),
]