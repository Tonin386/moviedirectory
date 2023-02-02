from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from django.conf.urls import url
from main.views import *
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('<int:page>', views.home_page, name="home_page"),
    path('register', views.register, name="register"),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    path('reactivate', views.reactivate, name='reactivate'),
    path('watchlist', views.watchlist, name="watchlist"),
    path('watchlist/edit/<int:pk>', WatchedMovieUpdate.as_view(), name="watchedmovie_edit"),
    path('watchlist/delete/<str:ownid>', views.delete, name="delete"),
    path('watchlist/browse/<str:username>', views.user_watchlist, name="user_watchlist"),
    path('movielist', views.movielist, name="movielist"),
    path('movielist/add/<str:imdbid>', views.add, name="add"),
    path('more/<int:pk>', WatchedMovieDetailView.as_view(), name='watchedmovie-detail'),
    path('profile', views.profile, name="profile"),
    path('friendlist', views.friendlist, name="friendlist"),
    path('friendlist/delete/<int:friend_id>', views.delete_friend, name="delete_friend"),
    path('friendlist/accept/<int:friend_id>', views.accept_friend, name="accept_friend"),
    path('friendlist/refuse/<int:friend_id>', views.refuse_friend, name="refuse_friend"),
    path('friendlist/cancel/<int:friend_id>', views.cancel_friend, name="cancel_friend"),
    # url(r'stats/(.*)', views.stats, name="stats"),
    path("stats/", views.stats, name="stats")
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns