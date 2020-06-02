from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import ugettext as _, get_language
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseNotFound, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_text
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.views.generic.edit import UpdateView
from django.shortcuts import render, redirect
from .tokens import account_activation_token
from django.views.generic import DetailView
from django.template import RequestContext
from django.core.mail import send_mail
from moviedirectory.models import *
from .utilities import send_invite
from django.db.models import Q
from datetime import datetime
from .forms import *
from .api import *
import logging


logger = logging.getLogger(__name__)


def logout(request):
	dj_logout(request)

	return redirect('/')

def register(request):
	form = SignInForm(request.POST or None)
	addedUser = False
	errorThrowed = True

	if form.is_valid():
		new_user = form.save()
		new_user.is_active = False
		new_user.save()
		current_site = get_current_site(request)
		mail_subject = _("Activate your MovieDirectory account")
		message = render_to_string('mail/acc_active_email.html', {
			'user': new_user,
			'domain': current_site.domain,
			'uid':urlsafe_base64_encode(force_bytes(new_user.pk)),
			'token':account_activation_token.make_token(new_user),
		})
		to_email = form.cleaned_data.get('email')
		send_mail(
			mail_subject,
			message,
			"\"Movie Directory\" <support@movie-directory.com>",
			[to_email],
			html_message=message
		)
		errorThrowed = False
		addedUser = True
		logger.info(new_user.username + " signed in.")

	return render(request, 'auth/register.html', locals())

def reactivate(request):
	if request.user.is_authenticated:
		return redirect('home')

	post = False
	if request.POST:
		post = True
		if request.POST['email']:
			try:
				inactive_user = User.objects.get(email=request.POST['email'])
			except ObjectDoesNotExist:
				exist = False
				return render(request, 'auth/reactivate.html', locals())

			exist = True
			if inactive_user.is_active:
				active = True
				return render(request, 'auth/reactivate.html', locals())
			else:
				active = False
				current_site = get_current_site(request)
				mail_subject = _("Activate your MovieDirectory account")
				message = render_to_string('mail/acc_active_email.html', {
					'user': inactive_user,
					'domain': current_site.domain,
					'uid':urlsafe_base64_encode(force_bytes(inactive_user.pk)),
					'token':account_activation_token.make_token(inactive_user),
				})
				to_email = request.POST['email']
				send_mail(
					mail_subject,
					message,
					"\"Movie Directory\" <support@movie-directory.com>",
					[to_email],
					html_message=message
				)
				errorThrowed = False
				addedUser = True
				logger.info(user.username + " asked to send again email activation.")

	return render(request, 'auth/reactivate.html', locals())



def activate(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		new_user = User.objects.get(pk=int(uid))
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	if new_user is not None and account_activation_token.check_token(new_user, token):
		new_user.is_active = True
		new_user.save()
		dj_login(request, new_user)
		logger.info(new_user.username +" activated his account.")
		send_mail(
			new_user.username + " activated his account",
			"A new user just activated his account on " + datetime.now().strftime('%d/%m/%Y %H:%M:%S') + ".\nUsername: " + new_user.username,
			"\"Movie Directory accounts\" <support@movie-directory.com>",
			["support@movie-directory.com"]
		)
		return redirect('home')
	else:
		logger.error("Invalid activation link for "+ uid)
		return HttpResponse(_('Activation link is invalid!'))

@login_required
def watchlist(request):
		
	movies = WatchedMovie.objects.filter(viewer=request.user).order_by('-view_date', '-id')[:20]
	page = 1
	nb_elements = len(WatchedMovie.objects.filter(viewer=request.user))
	next_page = 2
	previous_page = 1 
	
	if page*20 < nb_elements:
		last_page = False
	else:
		last_page = True

	return render(request, 'pages/watchlist.html', locals())

@login_required
def watchlist_page(request, page):
	if page < 2:
		return redirect('watchlist')

	start = (page-1) * 20
	end = page*20
	movies = WatchedMovie.objects.filter(viewer=request.user).order_by('-view_date', '-id')[start:end]
	nb_elements = len(WatchedMovie.objects.filter(viewer=request.user))
	next_page = page+1
	previous_page = page-1
	
	if page*20 < nb_elements:
		last_page = False
	else:
		last_page = True

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
		logger.error("user '"+t_user+"' doesn't exist")
		return redirect('home')

	movies = WatchedMovie.objects.filter(viewer=t_user).order_by('-view_date', '-id')[:10]
	page = 1
	nb_elements = len(WatchedMovie.objects.filter(viewer=t_user))
	next_page = 2
	previous_page = 1 
	
	if page*10 < nb_elements:
		last_page = False
	else:
		last_page = True

	friend_requests_received = t_user.get_received_friend_requests_id()

	if request.POST:
		output = send_invite(t_user, request.user)

		t_user.save()
		request.user.save()

		friend_requests_received = t_user.get_received_friend_requests_id()

		return render(request, 'pages/user_watchlist.html', locals())


	return render(request, 'pages/user_watchlist.html', locals())

def user_watchlist_page(request, username, page):
	if page < 2:
		return redirect('user_watchlist', username=username)

	error = False

	try:
		t_user = User.objects.get(username=username)
		t_friends = t_user.friends.all()
		if t_user == request.user:
			return redirect('watchlist')
	except ObjectDoesNotExist:
		error = True
		logger.error("user '"+t_user+"' doesn't exist")
		return render(request, 'pages/user_watchlist.html', locals())

	start = (page-1) * 10
	end = page*10
	movies = WatchedMovie.objects.filter(viewer=t_user).order_by('-view_date', '-id')[start:end]
	nb_elements = len(WatchedMovie.objects.filter(viewer=t_user))
	next_page = page+1
	previous_page = page-1
	
	if page*10 < nb_elements:
		last_page = False
	else:
		last_page = True


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
			logger.info("Api request success for "+ title)
		else:
			success = False
			logger.error("Bad api request for "+ title)

	return render(request, 'pages/movielist.html', locals())

@login_required
def add(request, imdbid):
	movie, created = Movie.objects.get_or_create(imdbid=imdbid)

	if created:
		movie.fetch()

	now = datetime.today().strftime('%Y-%m-%d')

	form = WatchedMovieForm(request.POST or None, movie)

	if not movie.title:
		logger.error("Tried to add movie without title.")
		return redirect('movielist')

	if form.is_valid():
		form.movie = movie
		form.user = request.user
		form.save()
		logger.info("Added "+movie.title+" to "+request.user.username+"'s watchlist")
		return redirect('watchlist')


	return render(request, 'pages/add.html', locals())

@login_required
def delete(request, ownid):
	try:
		toDel = WatchedMovie.objects.get(id=ownid)
		if request.user == toDel.viewer:
			logger.info(toDel.viewer.username + " deleted WatchedMovie "+ toDel.movie.title)
			toDel.delete()
		return redirect('watchlist')
	except ObjectDoesNotExist:
		logger.error("Tried to delete unexisting WatchedMovie with id="+str(ownid))
		return redirect('watchlist')


@login_required
def profile(request):
	edit_form = EditProfileForm(request.POST or None)

	if request.user.birth_date:
		birthday = request.user.birth_date.strftime('%Y-%m-%d')

	current_language = get_language()

	if request.POST: #If request is a form
		if edit_form.is_valid() and request.POST.get('from_edit_profile', False): #Is it the edit profile form?
			data = edit_form.cleaned_data
			request.user.first_name = data['first_name']
			request.user.last_name = data['last_name']
			request.user.birth_date = data['birth_date']
			request.user.private = data['private']
			request.user.email_notifications = data['email_notifications']
			request.user.name_display = data['name_display']
			request.user.save()
			success = True
			logger.info(request.user.username + " updated his profile.")

	return render(request, 'pages/profile.html', locals())

@login_required
def friendlist(request):
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
		username = request.POST['username']
		try:
			asked_user = User.objects.get(username=username) #Can we find this user?
		except ObjectDoesNotExist: #No? Alright. Abort.
			logger.error(request.user.username + " tried to send an invite to " + username + " but this user doesn't exist.")
			output = _("This user doesn't exist")
			return render(request, 'pages/friendlist.html', locals())

		output = send_invite(asked_user, request.user)
		user_sent_id = request.user.get_sent_friend_requests_id()
		user_received_id = request.user.get_received_friend_requests_id()
		user_sent = []
		user_received = []
		for user_id in user_sent_id:
			user_sent.append(User.objects.get(id=user_id))
		for user_id in user_received_id:
			user_received.append(User.objects.get(id=user_id))

		request.user.save()
		asked_user.save()

	return render(request, 'pages/friendlist.html', locals())

@login_required
def delete_friend(request, friend_id):
	try:
		old_friend = User.objects.get(id=friend_id)
	except ObjectDoesNotExist:
		return HttpResponse("You shouldn't be here!")

	request.user.friends.remove(old_friend)
	old_friend.friends.remove(request.user)

	logger.info(request.user.username + " deleted " + old_friend.username + " from his friendlist")

	return redirect('friendlist')

@login_required
def accept_friend(request, friend_id):
	try:
		friend = User.objects.get(id=friend_id)
	except ObjectDoesNotExist:
		return HttpResponse("You shouldn't be here!")

	user_received_id = request.user.get_received_friend_requests_id()
	user_received_id.remove(friend.id)
	request.user.received_friend_requests = " ".join(str(v) for v in user_received_id)

	friend_sent_id = friend.get_sent_friend_requests_id()
	friend_sent_id.remove(request.user.id)
	friend.sent_friend_requests = " ".join(str(v) for v in friend_sent_id)

	friend.friends.add(request.user)
	request.user.friends.add(friend)

	request.user.save()
	friend.save()

	if request.user.email_notifications:
		mail_subject = _("You have a new friend!")
		message = _("You are now friend with ") + friend.username + _("!\nYou can now see this user's watchlist.\n\n\nYou can turn off email notifications on your profile.")
		to_email = request.user.email

		send_mail(
			mail_subject,
			message,
			"\"Movie Directory\" <support@movie-directory.com>",
			[to_email],
			html_message=message
		)

	if friend.email_notifications:
		mail_subject = _("You have a new friend!")
		message = _("You are now friend with ") + request.user.username + _("!\nYou can now see this user's watchlist.\n\n\nYou can turn off email notifications on your profile.")
		to_email = friend.email

		send_mail(
			mail_subject,
			message,
			"\"Movie Directory\" <support@movie-directory.com>",
			[to_email],
			html_message=message
		)

	logger.info(request.user.username + " and " + friend.username + " are now friends.")

	return redirect('friendlist')

@login_required
def refuse_friend(request, friend_id):
	try:
		friend = User.objects.get(id=friend_id)
	except ObjectDoesNotExist:
		return HttpResponse("You shouldn't be here!")

	user_received_id = request.user.get_received_friend_requests_id()
	user_received_id.remove(friend.id)
	request.user.received_friend_requests = " ".join(str(v) for v in user_received_id)

	friend_sent_id = friend.get_sent_friend_requests_id()
	friend_sent_id.remove(request.user.id)
	friend.sent_friend_requests = " ".join(str(v) for v in friend_sent_id)

	request.user.save()
	friend.save()

	logger.info(request.user.username + "doesn't want to be friend with " + friend.username)

	return redirect('friendlist')

@login_required
def cancel_friend(request, friend_id):
	try:
		friend = User.objects.get(id=friend_id)
	except ObjectDoesNotExist:
		return HttpResponse("You shouldn't be here!")

	user_sent_id = request.user.get_sent_friend_requests_id()
	user_sent_id.remove(friend.id)
	request.user.sent_friend_requests = " ".join(str(v) for v in user_sent_id)

	friend_received_id = friend.get_received_friend_requests_id()
	friend_received_id.remove(request.user.id)
	friend.received_friend_requests = " ".join(str(v) for v in friend_received_id)

	request.user.save()
	friend.save()

	logger.info(request.user.username + " canceled his friend invite to " + friend.username)

	return redirect('friendlist')


def home(request):

	all_movies = WatchedMovie.objects.all().order_by('-view_date', '-id')
	movies = []
	for movie in all_movies:
		if movie.viewer.private:
			if movie.viewer == request.user or request.user in movie.viewer.friends.all():
				movies.append(movie)
		else:
			movies.append(movie)

	community = movies[:10]
	nb_movies = len(movies)
	page = 1
	next_page = 2
	previous_page = 1 

	if page*10 < nb_movies:
		last_page = False
	else:
		last_page = True

	return render(request, 'index.html', locals())

def home_page(request, page):
	if page < 2:
		return redirect('home')

	all_movies = WatchedMovie.objects.all().order_by('-view_date', '-id')
	movies = []
	for movie in all_movies:
		if movie.viewer.private:
			if movie.viewer == request.user or request.user in movie.viewer.friends.all():
				movies.append(movie)
		else:
			movies.append(movie)

	start = (page-1) * 10
	end = page*10
	community =  movies[start:end]
	nb_movies = len(movies)
	next_page = page+1
	previous_page = page-1

	if page*10 < nb_movies:
		last_page = False
	else:
		last_page = True

	return render(request, 'index.html', locals())

class WatchedMovieDetailView(DetailView):
	model = WatchedMovie
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['now'] = timezone.now()
		return context


class WatchedMovieUpdate(UpdateView):
	model = WatchedMovie
	fields = ['view_date', 'note', 'new', 'theater', 'comment']
	template_name_suffix = '_update_form'