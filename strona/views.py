import time
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
auth = firebase.auth()
database = firebase.database()
 
 
def login_navbar(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            user_id = user['localId']
            username = str(database.child("users").child(user_id).child("username").get())
            request.session['user_id'] = user_id
            request.session['user_email'] = email
            request.session['user_name'] = username
            messages.success(request, 'Logged in successfully.')
            return redirect('mainpage')
        except Exception as e:
            messages.error(request, 'Invalid credentials, please try again.')
            return redirect('mainpage')
    return redirect('mainpage')
 
def logout(request):
    try:
        print("Logging out user:", request.session.get('user_name'))
        request.session.pop('user_id', None)
        request.session.pop('user_email', None)
        request.session.pop('user_name', None)
        print("User logged out successfully")

    except KeyError as e:
        print("Error while logging out:", e)
        pass
    messages.success(request, 'Logged out successfully.')
    return redirect('mainpage')
 
 
 
def mainpage(request):
    username = request.session.get('user_name')
 
    return render(request, 'mainPage.html', {'user_name': username})
 
 
def register(request):
    username = request.session.get('user_name')
    if request.method == 'POST':
        username = request.POST.get('register_username')
        email = request.POST.get('register_email')
        password = request.POST.get('register_password')

        try:
            user = auth.create_user_with_email_and_password(email, password)

        except Exception as e:
            messages.error(request, str(e))
            return redirect('register')
        

        for attempt in range(5):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                break  
            except Exception as e:
                time.sleep(2)


        try:
            
            user_id = user['localId']
            request.session['user_id'] = user_id
            request.session['user_email'] = email
            request.session['user_name'] = username
            database.child("users").child(user_id).child("username").set(username)
            messages.success(request, 'Account registered successfully.')
 
            return redirect('mainpage')
        
        except Exception as e:
            messages.error(request, str(e))
            return redirect('register')
        
    return render(request, 'register.html', {'user_name': username})
 
def login(request):
    username = request.session.get('user_name')
    if request.method == 'POST':
        email = request.POST.get('login_email')
        password = request.POST.get('login_password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            user_id = user['localId']
            username = database.child("users").child(user_id).child("username").get().val()
            request.session['user_id'] = user_id
            request.session['user_name'] = username
            request.session['user_email'] = email
            messages.success(request, 'Account logged in.')
 
            return redirect('mainpage')
        except Exception as e:
            print(f"error", e)
            return redirect('login')
    return render(request, 'login.html', {'user_name': username})
 
 
 
 
def create(request):
    username = request.session.get('user_name')
    user_id = request.session.get('user_id')

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
                database.child("games").child(game_id).child("user_id").set(user_id)
                messages.success(request, "Game created successfully!")
                return redirect('add_pics', game_id=game_id)
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return redirect('create')
    else:
        form = GameForm()
 
    return render(request, 'create.html', {'form': form, 'user_name': username})
 
 
def add_pics(request, game_id):
    username = request.session.get('user_name')
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
 
    return render(request, 'add_pics.html', {"form": form, 'game_id': game_id, 'upload_count': current_upload_count, 'user_name': username})