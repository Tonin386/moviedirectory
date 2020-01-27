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
		
	movies = WatchedMovie.objects.filter(viewer=request.user).order_by('-view_date')[:3]

	return render(request, 'pages/watchlist.html', locals())

@login_required
def watchlist_page(request, page):
	if page < 2:
		return redirect('watchlist')

	start = (page-1) * 3
	end = page*3
	movies = WatchedMovie.objects.filter(viewer=request.user).order_by('-view_date')[start:end]

	return render(request, 'pages/watchlist.html', locals())

def user_watchlist(request, username):
	error = False

	try:
		t_user = User.objects.get(username=username)
		t_friends = t_user.friends.all()
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
	edit_form = EditProfileForm(request.POST or None)

	birthday = request.user.birth_date.strftime('%Y-%m-%d')

	current_language = get_language()

	user_friends = request.user.friends.all()

	user_sent_id = request.user.get_sent_friend_requests_id()
	user_sent = []
	for user_id in user_sent_id:
		user_sent.append(User.objects.get(id=user_id))

	user_received_id = request.user.get_received_friend_requests_id()
	user_received = []
	for user_id in user_received_id:
		user_received.append(User.objects.get(id=user_id))

	if request.POST: #If request is a form
		if edit_form.is_valid() and request.POST.get('from_edit_profile', False): #Is it the edit profile form?
			user = request.user
			data = edit_form.cleaned_data
			user.first_name = data['first_name']
			user.last_name = data['last_name']
			user.birth_date = data['birth_date']
			user.private = data['private']
			user.email_notifications = data['email_notifications']
			user.name_display = data['name_display']
			user.save()
			success = True
		elif request.POST.get('from_send_invite', False): #If it isn't, it has to be the send request form.
			username = request.POST['username']
			try:
				asked_user = User.objects.get(username=username) #Can we find this user?
			except ObjectDoesNotExist: #No? Alright. Abort.
				return redirect("profile")

			if not asked_user in request.user.friends.all() and asked_user != request.user: #We check if we aren't already friend with him.
				asked_user_received_id = asked_user.get_received_friend_requests_id() #We found him. Let's see if he already is somewhere

				if not request.user.id in asked_user_received_id and not asked_user.id in user_sent_id: #Checking we haven't already sent an invite to this user
					asked_user_sent_id = asked_user.get_sent_friend_requests_id()

					if request.user.id in asked_user_sent_id: #He also sent us an invite! I think we want to be friend
						request.user.friends.add(asked_user)
						asked_user.friends.add(request.user)
						asked_user_sent_id.remove(request.user.id)
						user_received_id.remove(asked_user.id)
						asked_user.sent_friend_requests = " ".join(asked_user_sent_id)
						request.user.received_friend_requests = " ".join(user_received_id)
						asked_user.save()
						request.user.save()
						#Send a mail to both users
					else: #Alright, we don't know yet if he wants to be friend with us.
						if asked_user.received_friend_requests != "":
							asked_user.received_friend_requests += " " + str(request.user.id)
						else:
							asked_user.received_friend_requests = str(request.user.id)

						if request.user.sent_friend_requests != "":
							request.user.sent_friend_requests += " " + str(asked_user.id)
						else:
							request.user.sent_friend_requests = str(asked_user.id)

						asked_user.save()
						request.user.save()
						#Send a mail to the user

			return redirect('profile')



	return render(request, 'pages/profile.html', locals())

@login_required
def delete_friend(request, friend_id):
	try:
		old_friend = User.objects.get(id=friend_id)
	except ObjectDoesNotExist:
		return HttpResponse("You shouldn't be here!")

	request.user.friends.remove(old_friend)
	old_friend.friends.remove(request.user)

	return redirect('profile')

@login_required
def accept_friend(request, friend_id):
	try:
		friend = User.objects.get(id=friend_id)
	except ObjectDoesNotExist:
		return HttpResponse("You shouldn't be here!")

	user_received_id = request.user.get_received_friend_requests_id()
	user_received_id.remove(friend.id)
	request.user.received_friend_requests = " ".join(user_received_id)

	friend_sent_id = friend.get_sent_friend_requests_id()
	friend_sent_id.remove(request.user.id)
	friend.sent_friend_requests = " ".join(friend_sent_id)

	friend.friends.add(request.user)
	request.user.friends.add(friend)

	request.user.save()
	friend.save()

	return redirect('profile')

@login_required
def refuse_friend(request, friend_id):
	try:
		friend = User.objects.get(id=friend_id)
	except ObjectDoesNotExist:
		return HttpResponse("You shouldn't be here!")

	user_received_id = request.user.get_received_friend_requests_id()
	user_received_id.remove(friend.id)
	request.user.received_friend_requests = " ".join(user_received_id)

	friend_sent_id = friend.get_sent_friend_requests_id()
	friend_sent_id.remove(request.user.id)
	friend.sent_friend_requests = " ".join(friend_sent_id)

	request.user.save()
	friend.save()

	return redirect('profile')

@login_required
def cancel_friend(request, friend_id):
	try:
		friend = User.objects.get(id=friend_id)
	except ObjectDoesNotExist:
		return HttpResponse("You shouldn't be here!")

	user_sent_id = request.user.get_sent_friend_requests_id()
	user_sent_id.remove(friend.id)
	request.user.sent_friend_requests = " ".join(user_sent_id)

	friend_received_id = friend.get_received_friend_requests_id()
	friend_received_id.remove(request.user.id)
	friend.received_friend_requests = " ".join(friend_received_id)

	request.user.save()
	friend.save()

	request.user.save()
	friend.save()

	return redirect('profile')


def home(request):

	community = WatchedMovie.objects.order_by('-view_date')[:10]

	return render(request, 'index.html', locals())

def home_page(request, page):
	if page < 2:
		return redirect('home')

	start = (page-1) * 10
	end = page*10
	community = WatchedMovie.objects.order_by('-view_date')[start:end]

	return render(request, 'index.html', locals())
