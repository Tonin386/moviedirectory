from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('register', views.register, name="register"),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    path('watchlist', views.watchlist, name="watchlist"),
    path('watchlist/delete/<str:ownid>', views.delete, name="delete"),
    path('watchlist/browse/<int:user_id>', views.user_watchlist, name="user_watchlist"),
    path('movielist', views.movielist, name="movielist"),
    path('movielist/add/<str:imdbid>', views.add, name="add"),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^login/', views.login, name="login"),
]
