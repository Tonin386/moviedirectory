from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('register', views.register, name="register"),
    path('watchlist', views.watchlist, name="watchlist"),
    path('movielist', views.movielist, name="movielist"),
    path('movielist/add/<str:imdbid>', views.add, name="add"),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^login/', views.login, name="login"),
]
