from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from firebase_admin import auth
import pyrebase
from .forms import GameForm, UploadFileForm
import random, string

from datetime import datetime
from zoneinfo import ZoneInfo



config={
    "apiKey": "AIzaSyC2Jg3HI7jpGeukh0EgXmrb11GbBBnWMTQ",
    "authDomain": "stronaww123.firebaseapp.com",
    "databaseURL": "https://stronaww123-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "stronaww123",
    "storageBucket": "stronaww123.appspot.com",
    "messagingSenderId": "358939997824",
    "appId": "1:358939997824:web:73bef249ea412d35f31865",
#    measurementId: "G-PE8N920P01"
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()


def login_navbar(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = authe.sign_in_with_email_and_password(email, password)
            token = user['idToken']
            user_info = authe.get_account_info(token)
            user_id = user_info['users'][0]['localId']
            request.session['user_id'] = user_id
            request.session['user_email'] = email
            messages.success(request, 'Logged in successfully.')
            return redirect('mainpage')
        except Exception as e:
            messages.error(request, 'Invalid credentials, please try again.')
            return redirect('mainpage')
    return redirect('mainpage')

def logout(request):
    try:
        del request.session['user_id']
        del request.session['user_email']
    except KeyError:
        pass
    messages.success(request, 'Logged out successfully.')
    return redirect('mainpage')



def mainpage(request):
    user_email = request.session.get('user_email')

    return render(request, 'mainPage.html', {'user_email': user_email})


def register(request):
    user_email = request.session.get('user_email')
    if request.method == 'POST':
        email = request.POST.get('register_email')
        password = request.POST.get('register_password')
        try:
            user = authe.create_user_with_email_and_password(email, password)
            messages.success(request, 'Account registered successfully.')

            return redirect('mainpage')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('register')
    return render(request, 'register.html', {'user_email': user_email})

def login(request):
    user_email = request.session.get('user_email')
    if request.method == 'POST':
        email = request.POST.get('login_email')
        password = request.POST.get('login_password')
        try:
            user = authe.sign_in_with_email_and_password(email, password)
            token = user['idToken']
            messages.success(request, 'Account logged in.')

            return redirect('mainpage')
        except Exception as e:
            return redirect('login')
    return render(request, 'login.html', {'user_email': user_email})


    

def create(request):
    user_email = request.session.get('user_email')
    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            number_of_choices = form.cleaned_data['number_of_choices']

            game_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

            
            game_data = {
                "title": title,
                "number_of_choices": number_of_choices
            }

            try:
                poland_time = datetime.now(ZoneInfo('Europe/Warsaw'))
                formatted_time = poland_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
                database.child("games").child(game_id).set(game_data)
                database.child("games").child(game_id).child("date").set(formatted_time)
                messages.success(request, "Game created successfully!")
                return redirect('add_pics', game_id=game_id)
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return redirect('create')
    else:
        form = GameForm()

    return render(request, 'create.html', {'form': form, 'user_email': user_email})


def add_pics(request, game_id):
    user_email = request.session.get('user_email')
    game = database.child("games").child(game_id).get().val()
    if not game:
        messages.error(request, "Invalid game ID.")
        return redirect('mainpage')

    number_of_choices = game.get('number_of_choices', 0)
    current_upload_count = request.session.get(f'upload_count_{game_id}', 0)
    next_upload_count = current_upload_count + 1


    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            file = request.FILES['file']

            try:
                storage = firebase.storage()
                img_name = str(current_upload_count) + "_" + title
                file_path = f"images/{game_id}/{img_name}.png"
                storage.child(file_path).put(file)

                image_data = {
                    "name": title,
                    "file_path": file_path
                }
                

                current_upload_count += 1
                request.session[f'upload_count_{game_id}'] = current_upload_count

                if current_upload_count < int(number_of_choices):
                    messages.success(request, f"Image {current_upload_count} uploaded successfully! Please upload the next image.")
                    return redirect('add_pics', game_id=game_id)
                else:
                    messages.success(request, "All images uploaded successfully!")
                    del request.session[f'upload_count_{game_id}']
                    return redirect('mainpage')
            except Exception as e:
                messages.error(request, f"Error uploading image: {str(e)}")
                return redirect('add_pics', game_id=game_id)
    else:
        form = UploadFileForm()

    return render(request, 'add_pics.html', {"form": form, 'game_id': game_id, 'upload_count': current_upload_count, 'user_email': user_email})