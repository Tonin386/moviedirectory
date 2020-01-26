from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import ugettext as _, get_language
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseNotFound, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_text
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from .tokens import account_activation_token
from django.template import RequestContext
from django.core.mail import EmailMessage
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
		user = form.save()
		user.is_active = False
		user.save()
		current_site = get_current_site(request)
		mail_subject = _("Activate your MovieDirectory account")
		message = render_to_string('mail/acc_active_email.html', {
			'user': user,
			'domain': current_site.domain,
			'uid':urlsafe_base64_encode(force_bytes(user.pk)),
			'token':account_activation_token.make_token(user),
		})
		to_email = form.cleaned_data.get('email')
		email = EmailMessage(
			mail_subject, message, to=[to_email]
		)
		email.send()
		print("Email sent to "+ to_email)
		errorThrowed = False
		addedUser = True

	return render(request, 'auth/register.html', locals())

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=int(uid))
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        dj_login(request, user)
        return redirect('home')
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse(_('Activation link is invalid!' + uid))

@login_required
def watchlist(request):
		
	movies = WatchedMovie.objects.filter(viewer=request.user).order_by('-view_date')

	return render(request, 'pages/watchlist.html', locals())

def user_watchlist(request, user_id):
	error = False

	try:
		t_user = User.objects.get(id=user_id)
		if t_user == request.user:
			return redirect('watchlist')
	except ObjectDoesNotExist:
		error = True
		return render(request, 'pages/user_watchlist.html', locals())

	movies = WatchedMovie.objects.filter(viewer=t_user).order_by('-view_date')
	return render(request, 'pages/user_watchlist.html', locals())

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


	return render(request, 'pages/add.html', locals())

@login_required
def delete(request, ownid):
	try:
		toDel = WatchedMovie.objects.get(id=ownid)
		if request.user == toDel.viewer:
			toDel.delete()
		return redirect('watchlist')
	except ObjectDoesNotExist:
		return redirect('watchlist')


@login_required
def profile(request):
	form = EditProfileForm(request.POST or None)
	birthday = request.user.birth_date.strftime('%Y-%m-%d')
	current_language = get_language()
	print(current_language)

	if form.is_valid():
		user = request.user
		data = form.cleaned_data
		user.first_name = data['first_name']
		user.last_name = data['last_name']
		user.birth_date = data['birth_date']
		user.private = data['private']
		user.email_notifications = data['email_notifications']
		user.name_display = data['name_display']
		user.save()
		print(user.name_display)
		print(data['name_display'])
		success = True

	return render(request, 'pages/profile.html', locals())


def home(request):

	community = WatchedMovie.objects.order_by('-view_date')[:10]

	return render(request, 'index.html', locals())