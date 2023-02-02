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
from datetime import datetime, timedelta
from django.core.mail import send_mail
from moviedirectory.models import *
from plotly.offline import plot
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from django.db.models import Q
import plotly.graph_objs as go
import plotly.express as px
from .utilities import *
from .forms import *
from .api import *
import numpy as np
import base64
import io




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
			'domain': 'movie-directory.com',
			'uid':urlsafe_base64_encode(force_bytes(new_user.pk)),
			'token':account_activation_token.make_token(new_user),
		})
		to_email = form.cleaned_data.get('email')
		send_mail(
			mail_subject,
			message,
			"\"Movie Directory\" <moviedirectory@movie-directory.com>",
			[to_email],
			html_message=message,
			fail_silently=False
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
				print(current_site)
				mail_subject = _("Activate your MovieDirectory account")
				message = render_to_string('mail/acc_active_email.html', {
					'user': inactive_user,
					'domain': 'movie-directory.com',
					'uid':urlsafe_base64_encode(force_bytes(inactive_user.pk)),
					'token':account_activation_token.make_token(inactive_user),
				})
				to_email = request.POST['email']
				send_mail(
					mail_subject,
					message,
					"\"Movie Directory\" <moviedirectory@movie-directory.com>",
					[to_email],
					html_message=message,
					fail_silently=False
				)
				errorThrowed = False
				addedUser = True
				logger.info(inactive_user.username + " asked to send again email activation.")

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
	allMovies = WatchedMovie.objects.filter(viewer=request.user).order_by('-view_date', '-id')
	typeRadio = ""
	if request.POST:
		typeRadio = request.POST["typeRadio"]
		inputText = request.POST["inputText"]

	if typeRadio == "title":
		allMovies_title = allMovies.filter(movie__title__regex=r"(?i)%s" % inputText)
		allMovies_title_fr = allMovies.filter(movie__title_fr__regex=r"(?i)%s" % inputText)
		allMovies_title_en = allMovies.filter(movie__title_en__regex=r"(?i)%s" % inputText)
		allMovies_title_ge = allMovies.filter(movie__title_ge__regex=r"(?i)%s" % inputText)

		movies = list(set(list(allMovies_title) + list(allMovies_title_en) + list(allMovies_title_fr) + list(allMovies_title_ge)))

	elif typeRadio == "director":
		movies = WatchedMovie.objects.filter(viewer=request.user).order_by('-view_date', '-id').filter(movie__director__regex=r"(?i)%s" % inputText)
	
	elif typeRadio == "releaseYear":
		movies = WatchedMovie.objects.filter(viewer=request.user).order_by('-view_date', '-id').filter(movie__year=inputText)

	elif typeRadio == "watchYear":
		try:
			inputText = int(inputText)
			movies = WatchedMovie.objects.filter(viewer=request.user).order_by('-view_date', '-id').filter(view_date__year=inputText)
		except:
			print("Error, search isn't a integer!")
	
	elif typeRadio == "with":
		movies = WatchedMovie.objects.filter(viewer=request.user).order_by('-view_date', '-id').filter(movie__actors__regex=r"(?i)%s" % inputText)

	elif typeRadio == "note":
		if inputText != "":
			regex = ""
			if inputText[0] == "<":
				try:
					regexText = int(inputText[1:])
					if regexText == 10:
						regex = r"^([0-9])$"
					elif regexText > 10:
						regex = r"^(([0-9])|(10))$"
					else:
						regex = r"^([0-%d])$" % regexText
				except:
					print("Error, search isn't a integer!")
			elif inputText[0] == ">":
				try:
					regexText = int(inputText[1:])
					if regexText == 10:
						regex = r"^11$"
					elif regexText > 10:
						regex = r"^11$"
					else:
						regex = r"^(([%d-9])|(10))$" % regexText
				except:
					print("Error, search isn't a integer!")
			else:
				regex = r"^%s$" % inputText

		movies = WatchedMovie.objects.filter(viewer=request.user).order_by('-view_date', '-id').filter(note__regex=regex)

	else:
		movies = WatchedMovie.objects.filter(viewer=request.user).order_by('-view_date', '-id')

	moviesShown = len(movies)
	total = len(allMovies)

	str1 = _("Listing")
	str21 = _("movies")
	str22 = _("movie")
	str3 = _("in total")

	if len(movies) > 1:
		spanText = "%s %d %s (%d %s)" % (str1, moviesShown, str21, total, str3)
	else:
		spanText = "%s %d %s (%d %s)" % (str1, moviesShown, str22, total, str3)

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

	movies = WatchedMovie.objects.filter(viewer=t_user).order_by('-view_date', '-id')

	friend_requests_received = t_user.get_received_friend_requests_id()

	if request.POST:
		output = send_invite(t_user, request.user)

		t_user.save()
		request.user.save()

		friend_requests_received = t_user.get_received_friend_requests_id()

		return render(request, 'pages/user_watchlist.html', locals())


	return render(request, 'pages/user_watchlist.html', locals())

@login_required
def stats(request):
	t_user = request.user
	f = WatchedMovie.objects.filter(viewer=t_user).order_by('view_date')[0].view_date.strftime("%Y-%m-%d")
	t = datetime.today().date().strftime("%Y-%m-%d")
	hashing_type ="months"
	if request.method == "GET" and request.GET:
		if "from" in request.GET.keys():
			f = request.GET['from'] if re.search(r'([0-9]){4}\-[0-1][0-9]\-[0-3][0-9]', request.GET['from']) else f

		if "to" in request.GET.keys():
			t = request.GET['to'] if re.search(r'([0-9]){4}\-[0-1][0-9]\-[0-3][0-9]', request.GET['to']) else t

		if "hashing_type" in request.GET.keys():
			hashing_type = request.GET['hashing_type'] if request.GET['hashing_type'] in ['weeks', 'months', 'years'] else "months"

	if(f != 0 and t != 0):
		if(datetime.strptime(f, '%Y-%m-%d') > datetime.strptime(t, '%Y-%m-%d')):
			f, t = t, f
		movies = WatchedMovie.objects.filter(viewer=t_user, view_date__range=[f, t])
	else:
		movies = WatchedMovie.objects.filter(viewer=t_user)

	notes = movies.values_list("note", flat=True)
	average_note = np.round(np.mean(notes))
	total = len(movies)

	actors = {}
	directors = {}
	writers = {}
	genres = {}
	languages = {}
	years = {}
	productions = {}
	lengths = []

	for m in movies:
		actors = countElements(m.movie.actors, actors)
		directors = countElements(m.movie.director, directors)
		writers = countElements(m.movie.writer, writers, True)
		genres = countElements(m.movie.genre, genres)
		languages = countElements(m.movie.language, languages)
		years = countElements(m.movie.year, years)
		productions = countElements(m.movie.production, productions)
		if m.movie.runtime != "N/A":
			lengths.append(int(m.movie.runtime.replace(" min", "")))
	#Nombres films vus par tranche de temps (années, mois, semaines). Films par réalisateurs, durée des films

	s_actors = sortDict(actors)
	s_directors = sortDict(directors)
	s_writers = sortDict(writers)
	s_genres = sortDict(genres)
	s_languages = sortDict(languages)
	s_years = sortDict(years)
	s_productions = sortDict(productions)

	average_runtime = np.round(int(np.mean(lengths)) / 60, 2)

	from_date = datetime.strptime(f, '%Y-%m-%d')
	to_date = datetime.strptime(t, '%Y-%m-%d')

	hash_dates, labels = createHashDatesArray(from_date, to_date, hashing_type)
	values = []
	for i in range(len(hash_dates) - 1):
		if not i:
			values.append(len(movies.filter(view_date__range=[hash_dates[i], hash_dates[i+1]])))
		else:
			values.append(len(movies.filter(view_date__range=[hash_dates[i] + timedelta(days=1), hash_dates[i+1]])))

	y_data = values

	wm_chart = px.line(x=labels, y=y_data, template="plotly_dark", text=y_data)

	wm_chart.update_traces(textposition="top center")
	config = {"displaylogo": False}
	wm_chart.update_layout(
		title={
		'text': _("Movies watched per %s" % hashing_type),
		'x': 0.5,
		'xanchor': 'center'
		},
		xaxis_title=_("Period of time"),
		xaxis_range=[0, 20],
		xaxis_rangeslider_visible=True,
		xaxis_fixedrange=False,
		yaxis_title=_("Movies watched"),
		yaxis_showticklabels=False,
		yaxis_range=[0, np.max(y_data)*1.1],
		yaxis_fixedrange=True,
		paper_bgcolor="rgba(15, 15, 15, 0.8)",
		plot_bgcolor="rgba(15, 15, 15, 0.8)",
		dragmode="pan",
		# font=dict(
		# 	size=16,
		# 	color="white"
		# )
	)

	div_wm_chart = wm_chart.to_html(config=config)

	genres_wc = WordCloud(
		background_color=None, 
		width=1000, 
		height=675,
		prefer_horizontal=0.95,
		mode="RGBA",
		max_words=25,
		random_state=2,
	)
	genres_wc.generate_from_frequencies(genres)
	genres_wc_url = wordcloudToUrl(genres_wc)

	directors_wc = WordCloud(
		background_color=None, 
		width=1000, 
		height=675,
		prefer_horizontal=0.8,
		mode="RGBA",
		max_words=50,
		random_state=2,
	)
	directors_wc.generate_from_frequencies(directors)
	directors_wc_url = wordcloudToUrl(directors_wc)

	actors_wc = WordCloud(
		background_color=None, 
		width=1000, 
		height=675,
		prefer_horizontal=0.80,
		mode="RGBA",
		max_words=50,
		random_state=2,
	)
	actors_wc.generate_from_frequencies(actors)
	actors_wc_url = wordcloudToUrl(actors_wc)

	
	return render(request, 'pages/stats.html', locals())


def movielist(request):
	title = ""

	if request.POST:
		title = request.POST["title"]

	if title:
		movies = make_request_search(title)
		success = True
		if movies != {}:
			movies = movies['Search']['results']
			logger.info("Api request success for "+ title)
		else:
			success = False
			logger.error("Bad api request for "+ title)

	return render(request, 'pages/movielist.html', locals())

@login_required
def add(request, imdbid):
	movie, created = Movie.objects.get_or_create(imdbid=imdbid)

	if created:
		print("fetching?")
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
			"\"Movie Directory\" <moviedirectory@movie-directory.com>",
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
			"\"Movie Directory\" <moviedirectory@movie-directory.com>",
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

	community = movies[:120]
	nb_movies = len(movies)
	page = 1
	next_page = 2
	previous_page = 1 

	if page*120 < nb_movies:
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

	start = (page-1) * 120
	end = page*120
	community =  movies[start:end]
	nb_movies = len(movies)
	next_page = page+1
	previous_page = page-1

	if page*12 < nb_movies:
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