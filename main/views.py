from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from django.template import RequestContext
from moviedirectory.models import User
from datetime import datetime
from .api import *
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
def watchlist(request):
		
	movies = WatchedMovie.objects.filter(viewer=request.user).order_by('-view_date')

	return render(request, 'pages/watchlist.html', locals())

def movielist(request):

	title = ""

	if request.POST:
		title = request.POST["title"]

	if title:
		movies = make_request_search(title)
		success = True
		if movies['Response'] == 'True':
			movies = movies['Search']
		else:
			success = False

	return render(request, 'pages/movielist.html', locals())

@login_required
def add(request, imdbid):
	movie, created = Movie.objects.get_or_create(imdbid=imdbid)

	if created:
		movie.fetch()

	now = datetime.today().strftime('%Y-%m-%d')

	form = WatchedMovieForm(request.POST or None, movie)

	if not movie.title:
		return redirect('movielist')

	if form.is_valid():
		form.movie = movie
		form.user = request.user
		form.save()
		return redirect('watchlist')
	else:
		print("Something went wrong")
		print(form.errors)

	return render(request, 'pages/add.html', locals())

@login_required
def delete(request, ownid):
	try:
		toDel = WatchedMovie.objects.get(id=ownid)
		if request.user == toDel.viewer:
			toDel.delete()
		return redirect('watchlist')
	except ObjectDoesNotExist:
		print("Object doesn't exist.")
		return redirect('watchlist')


			
def profile(request, username):
	user = User.objects.get(username=username)

	player = user.getPlayer()

	if not player == "error":
		return render(request, 'profile.html', locals())
	else:
		return HttpResponseNotFound()

def home(request):

	community = WatchedMovie.objects.order_by('-view_date')[:10]

	return render(request, 'index.html', locals())

# Create your views here.
