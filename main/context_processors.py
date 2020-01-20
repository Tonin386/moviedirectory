from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from main.forms import LoginForm
from moviedirectory.models import User

def login_form(request):
	if request.method == 'POST':
		loginForm = LoginForm(request.POST)
		if loginForm.is_valid():
			usr = loginForm.cleaned_data['username']
			pwd = loginForm.cleaned_data['password']
			user = authenticate(username=usr, password=pwd)
			if user:
				dj_login(request, user)
			else:
				error = True
		else:
			loginForm = LoginForm()
	return {
		'login_form' : LoginForm(request.POST or None)
	}