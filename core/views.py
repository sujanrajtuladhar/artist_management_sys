import csv

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db import connection
from django.shortcuts import render, redirect
from django.http import HttpResponse
from functools import wraps

from .forms import (
    UserForm, 
    UserUpdateForm,
    ArtistForm,
    ArtistUpdateForm,
    ArtistImportForm,
    MusicForm
    )


# Create your views here.


# Decorator Mixin
def super_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role_type != 'super_admin':
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def super_admin_and_artist_manager_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role_type not in ['super_admin', 'artist_manager']:
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def super_admin_and_artist_manager_and_artist_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role_type not in ['super_admin', 'artist_manager', 'artist']:
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def super_admin_and_artist_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role_type not in ['super_admin', 'artist']:
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# Views
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


@login_required
@super_admin_and_artist_manager_required
def artist_list(request):
    # List the user records with pagination [Role Access: super_admin]
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 1))

    with connection.cursor() as cursor:
        offset = (page - 1) * limit
        cursor.execute("SELECT name, dob, gender, address, first_release_year, no_of_albums_released, id FROM core_artist LIMIT %s OFFSET %s", (limit, offset))

        # fetch all
        artists = cursor.fetchall()
        # count total users
        cursor.execute("SELECT COUNT(*) FROM core_artist")
        total_artists = cursor.fetchone()[0]
        # calculate total pages
        total_pages = total_artists / limit
        # calculate next page
        next_page = page + 1 if page < total_pages else None
        # calculate prev page
        prev_page = page - 1 if page > 1 else None
        # calculate page range
        page_range = range(1, int(total_pages) + 1)

    # paginate artist with limit of 2 per page using cursor execute command
    artists_list = []
    for artist in artists:
        artist_dict = {
            'name': artist[0],
            'dob': artist[1],
            'gender': artist[2],
            'address': artist[3],
            'first_release_year': artist[4],
            'no_of_albums_released': artist[5],
            'id': artist[6]
        }
        artists_list.append(artist_dict)
    # return the list of artists with pagination details like page, limit, total_pages, next_page, prev_page
    context = {
        'artists': artists_list,
        'total_pages': int(total_pages),
        'page': page,
        'limit': limit,
        'next_page': int(next_page) if next_page else None,
        'prev_page': int(prev_page) if prev_page else None,
        'page_range': page_range,
    }

    return render(request, 'artist/artist_list.html', context)


@login_required
@super_admin_and_artist_manager_required
def create_artist(request):
    # Create a new user record [Role Access: super_admin]

    if request.method == 'POST':
        form = ArtistForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            dob = form.cleaned_data['dob']
            gender = form.cleaned_data['gender']
            address = form.cleaned_data['address']
            first_release_year = form.cleaned_data['first_release_year']
            no_of_albums_released = form.cleaned_data['no_of_albums_released']
            user = form.cleaned_data['user']

            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO core_artist (user_id, name, dob, gender, address, first_release_year, no_of_albums_released) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    [user.id, name, dob, gender, address, first_release_year, no_of_albums_released]
                )

            return redirect('core:artist_list')
    else:
        form = ArtistForm()

    return render(request, 'artist/create_artist.html', {'form': form})


@login_required
@super_admin_and_artist_manager_required
def update_artist(request, artist_id):
    # Update an existing artist record [Role Access: super_admin]

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, dob, gender, address, first_release_year, no_of_albums_released FROM core_artist WHERE id = %s", [artist_id])
        artist = cursor.fetchone()

    if not artist:
        return redirect('core:artist_list')

    if request.method == 'POST':
        form = ArtistUpdateForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            dob = form.cleaned_data['dob']
            gender = form.cleaned_data['gender']
            address = form.cleaned_data['address']
            first_release_year = form.cleaned_data['first_release_year']
            no_of_albums_released = form.cleaned_data['no_of_albums_released']

            with connection.cursor() as cursor:
                cursor.execute("UPDATE core_artist SET name = %s, dob = %s, gender = %s, address = %s, first_release_year = %s, no_of_albums_released = %s WHERE id = %s", [name, dob, gender, address, first_release_year, no_of_albums_released, artist_id])

            return redirect('core:artist_list')
    else:
        form = ArtistUpdateForm(initial={
            'name': artist[1],
            'dob': artist[2],
            'gender': artist[3],
            'address': artist[4],
            'first_release_year': artist[5],
            'no_of_albums_released': artist[6]
        })

    return render(request, 'artist/update_artist.html', {'form': form, 'artist': artist})


@login_required
@super_admin_and_artist_manager_required
def delete_artist(request, artist_id):
    # Delete an artist record [Role Access: super_admin]

    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM core_artist WHERE id = %s", [artist_id])
        artist = cursor.fetchone()

    if not artist:
        return redirect('core:artist_list')

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM core_artist WHERE id = %s", [artist_id])

    return redirect('core:artist_list')


@login_required
@super_admin_and_artist_manager_required
def import_artist_csv(request):

    if request.method == 'POST':
        form = ArtistImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                return redirect('core:import_artist_csv')

            # Read and process the CSV file
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            headers = next(reader)
            imported_artists = []

            for row in reader:
                name = row[0]
                dob = row[1]
                gender = row[2]
                address = row[3]
                first_release_year = row[4]
                no_of_albums_released = row[5]

                # Create the artist record
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO core_artist (name, dob, gender, address, first_release_year, no_of_albums_released) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        [name, dob, gender, address, first_release_year, no_of_albums_released]
                    )

                imported_artists.append(row)

            return redirect('core:artist_list')
    else:
        form = ArtistImportForm()

    return render(request, 'artist/import_artist_csv.html', {'form': form})


@login_required
@super_admin_and_artist_manager_required
def export_artist_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="artists.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Date of Birth', 'Gender', 'Address', 'First Release Year', 'Number of Albums Released'])

    with connection.cursor() as cursor:
        cursor.execute("SELECT name, dob, gender, address, first_release_year, no_of_albums_released FROM core_artist")
        artists = cursor.fetchall()

        for artist in artists:
            writer.writerow([
                artist[0],
                artist[1],
                artist[2],
                artist[3],
                artist[4],
                artist[5]
            ])

    return response


@login_required
@super_admin_and_artist_manager_and_artist_required
def song_list(request, artist_id):
    # Display the list of songs/music for a specific artist [Role Access: super_admin, admin]
    if request.user.role_type not in ['super_admin', 'admin']:
        return redirect('core:dashboard')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 1))

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, title, album_name FROM core_music WHERE artist_relation_id = %s", [artist_id])
        songs = cursor.fetchall()

        # count total songs
        cursor.execute("SELECT COUNT(*) FROM core_music")
        total_songs = cursor.fetchone()[0]
        # calculate total pages
        total_pages = total_songs / limit
        # calculate next page
        next_page = page + 1 if page < total_pages else None
        # calculate prev page
        prev_page = page - 1 if page > 1 else None
        # calculate page range
        page_range = range(1, int(total_pages) + 1)

    # paginate artist with limit of 2 per page using cursor execute command
    songs_list = []
    for song in songs:
        print(len(song))
        song_dict = {
            'id': song[0],
            'title': song[1],
            'album_name': song[2],
        }
        songs_list.append(song_dict)
    # return the list of songs with pagination details like page, limit, total_pages, next_page, prev_page
    context = {
        'songs': songs_list,
        'artist_id': artist_id,
        'total_pages': int(total_pages),
        'page': page,
        'limit': limit,
        'next_page': int(next_page) if next_page else None,
        'prev_page': int(prev_page) if prev_page else None,
        'page_range': page_range,
    }

    return render(request, 'music/song_list.html', context)


@login_required
@super_admin_and_artist_required
def create_song(request, artist_id):
    # Create a new song for a specific artist [Role Access: super_admin]
    if request.user.role_type != 'super_admin':
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = MusicForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            album_name = form.cleaned_data['album_name']
            genre = form.cleaned_data['genre']

            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO core_music (artist_relation_id, title, album_name, genre) VALUES (%s, %s, %s, %s)",
                               [artist_id, title, album_name, genre])

            return redirect('core:song_list', artist_id=artist_id)

    else:
        form = MusicForm()

    return render(request, 'music/create_song.html', {'form': form, 'artist_id': artist_id})


@login_required
@super_admin_and_artist_required
def update_song(request, artist_id, song_id):
    # Update an existing song [Role Access: super_admin]
    if request.user.role_type != 'super_admin':
        return redirect('core:dashboard')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, title, album_name, genre FROM core_music WHERE artist_relation_id = %s AND id = %s",
                       [artist_id, song_id])
        song = cursor.fetchone()

    if not song:
        return redirect('core:song_list', artist_id=artist_id)

    if request.method == 'POST':
        form = MusicForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            album_name = form.cleaned_data['album_name']
            genre = form.cleaned_data['genre']

            with connection.cursor() as cursor:
                cursor.execute("UPDATE core_music SET title = %s, album_name = %s, genre = %s WHERE artist_relation_id = %s AND id = %s",
                               [title, album_name, genre, artist_id, song_id])

            return redirect('core:song_list', artist_id=artist_id)

    else:
        form = MusicForm(initial={
            'title': song[1],
            'album_name': song[2],
            'genre': song[3]
        })

    return render(request, 'music/update_song.html', {'form': form, 'song': song, 'artist_id': artist_id})


@login_required
@super_admin_and_artist_required
def delete_song(request, artist_id, song_id):
    # Delete a song [Role Access: super_admin]
    if request.user.role_type != 'super_admin':
        return redirect('core:dashboard')

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM core_music WHERE artist_relation_id = %s AND id = %s", [artist_id, song_id])

    return redirect('core:song_list', artist_id=artist_id)