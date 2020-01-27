from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('<int:page>', views.home_page, name="home_page"),
    path('register', views.register, name="register"),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    path('watchlist', views.watchlist, name="watchlist"),
    path('watchlist/<int:page>', views.watchlist_page, name="watchlist_page"),
    path('watchlist/delete/<str:ownid>', views.delete, name="delete"),
    path('watchlist/browse/<str:username>', views.user_watchlist, name="user_watchlist"),
    path('watchlist/browse/<str:username>/<int:page>', views.user_watchlist_page, name="user_watchlist_page"),
    path('movielist', views.movielist, name="movielist"),
    path('movielist/add/<str:imdbid>', views.add, name="add"),
    path('profile', views.profile, name="profile"),
    path('profile/friend/delete/<int:friend_id>', views.delete_friend, name="delete_friend"),
    path('profile/friend/accept/<int:friend_id>', views.accept_friend, name="accept_friend"),
    path('profile/friend/refuse/<int:friend_id>', views.refuse_friend, name="refuse_friend"),
    path('profile/friend/cancel/<int:friend_id>', views.cancel_friend, name="cancel_friend"),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^login/', views.login, name="login"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns