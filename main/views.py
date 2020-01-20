from django.contrib.auth import logout as dj_logout
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from django.template import RequestContext
from moviedirectory.models import User
from .forms import *

def logout(request):
	dj_logout(request)

	return redirect('/')

def register(request):
	form = SignInForm(request.POST or None)
	addedUser = False
	errorThrowed = True

	if form.is_valid():
		form.save()
		errorThrowed = False
		addedUser = True

	return render(request, 'auth/register.html', locals())
			
def profile(request, username):
	active_tab = 5

	user = User.objects.get(username=username)

	player = user.getPlayer()

	if not player == "error":
		return render(request, 'profile.html', locals())
	else:
		return HttpResponseNotFound()

def home(request):
	return render(request, 'index.html', locals())

# Create your views here.
