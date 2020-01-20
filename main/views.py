from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from django.template import RequestContext
from moviedirectory.models import User
from .forms import *


def logout(request):
	dj_logout(request)

	return redirect('/')

def login(request):
	form = LoginForm(request.POST or None)
	if form.is_valid():
		usr = form.cleaned_data['username']
		pwd = form.cleaned_data['password']
		user = authenticate(username=usr, password=pwd)
		if user:
			dj_login(request, user)
			return redirect('home')
		else:
			error = True
	return render(request, 'auth/login.html', locals())


def register(request):
	form = SignInForm(request.POST or None)
	addedUser = False
	errorThrowed = True

	if form.is_valid():
		form.save()
		errorThrowed = False
		addedUser = True

	return render(request, 'auth/register.html', locals())

@login_required
def add_movie_to_watchlist(request):
	form = WatchedMovieForm(request.POST or None)
	user = request.user
	if form.is_valid():
		form.viewer = user
		form.save()
		return redirect('home')
	else:
		return render(request, 'pages/add_movie_to_watchlist.html', locals())

			
def profile(request, username):
	user = User.objects.get(username=username)

	player = user.getPlayer()

	if not player == "error":
		return render(request, 'profile.html', locals())
	else:
		return HttpResponseNotFound()

def home(request):
	return render(request, 'index.html', locals())

# Create your views here.
