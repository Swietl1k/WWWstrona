from django.urls import path
from . import views

urlpatterns = [
    path('mainpage/', views.mainpage, name='mainpage'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('login_navbar/', views.login_navbar, name='login_navbar'),
    path('logout/', views.logout, name='logout'),
    path('create/', views.create, name='create'),
    path('add_pics/<str:game_id>/', views.add_pics, name='add_pics'),
    path('find_category/<str:category>', views.find_category, name='find_category'),
    path('play/<str:game_id>', views.play, name='play'),
]