from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from typing import Any, List, Optional, Union
from wordcloud import STOPWORDS, WordCloud
from datetime import datetime, timedelta
from django.core.mail import send_mail
from moviedirectory.models import *
import matplotlib.pyplot as plt
from main.models import *
from PIL import Image
import urllib.parse
import pandas as pd
import logging
import re
import base64
import io
import os

logger = logging.getLogger(__name__)

def send_invite(asked_user, user):

	user_friends = user.friends.all()

	user_sent_id = user.get_sent_friend_requests_id()
	user_sent = []
	for user_id in user_sent_id:
		user_sent.append(User.objects.get(id=user_id))

	user_received_id = user.get_received_friend_requests_id()
	user_received = []
	for user_id in user_received_id:
		user_received.append(User.objects.get(id=user_id))

	if not asked_user in user.friends.all() and asked_user != user: #We check if we aren't already friend with him.
		asked_user_received_id = asked_user.get_received_friend_requests_id() #We found him. Let's see if he already is somewhere

		if not user.id in asked_user_received_id and not asked_user.id in user_sent_id: #Checking we haven't already sent an invite to this user
			asked_user_sent_id = asked_user.get_sent_friend_requests_id()

			if user.id in asked_user_sent_id: #He also sent us an invite! I think we want to be friend
				user.friends.add(asked_user)
				asked_user.friends.add(user)
				asked_user_sent_id.remove(user.id)
				user_received_id.remove(asked_user.id)
				asked_user.sent_friend_requests = " ".join(str(v) for v in asked_user_sent_id)
				user.received_friend_requests = " ".join(str(v) for v in user_received_id)
				asked_user.save()
				user.save()
				user.info(user.username + " and " + asked_user.username + " are now friends.")

				if user.email_notifications:
					mail_subject = _("You have a new friend!")
					message = _("You are now friend with ") + asked_user.username + _("!\nYou can now see this user's watchlist.\n\n\nYou can turn off email notifications on your profile.")
					to_email=user.email

					send_mail(
						mail_subject,
						message,
						"\"Movie Directory\" <support@movie-directory.com>",
						[to_email],
						html_message=message
					)

				if asked_user.email_notifications:
					mail_subject = _("You have a new friend!")
					message = _("You are now friend with ") + user.username + _("!\nYou can now see this user's watchlist.\n\n\nYou can turn off email notifications on your profile.")
					to_email = asked_user.email

					send_mail(
						mail_subject,
						message,
						"\"Movie Directory\" <support@movie-directory.com>",
						[to_email],
						html_message=message
					)

				return _("You are now friend with ") + asked_user.username

			else: #Alright, we don't know yet if he wants to be friend with us.
				if asked_user.received_friend_requests != "":
					asked_user.received_friend_requests += " " + str(user.id)
				else:
					asked_user.received_friend_requests = str(user.id)

				if user.sent_friend_requests != "":
					user.sent_friend_requests += " " + str(asked_user.id)
				else:
					user.sent_friend_requests = str(asked_user.id)

					logger.info(user.username + " sent a friend invite to " + asked_user.username)

					asked_user.save()
					user.save()

					if asked_user.email_notifications:
						mail_subject = _("You have a new friend invite!")
						message = user.username + _(" wants to be friend with you. You can accept or refuse this invite on Movie Directory.\n\n\nYou can turn off email notifications on your profile.")
						to_email = asked_user.email

						send_mail(
							mail_subject,
							message,
							"\"Movie Directory\" <support@movie-directory.com>",
							[to_email],
							html_message=message
						)

				return _("You sent a friend invite to ") + asked_user.username
		else:
			return _("You already sent a friend request to ") + asked_user.username
	else:
		return _("You are already friend with ") + asked_user.username

def countElements(toBeCounted, counted, special=False):
	if special:
		toBeCounted = re.sub(r" \(.*?\)", "", toBeCounted)

	for el in toBeCounted.split(', '):
		if el in counted.keys():
			counted[el] += 1
		else:
			counted[el] = 1

	counted.pop('N/A', None)

	return counted

def sortDict(d):
	return sorted(d.items(), key=lambda x:x[1], reverse=True)

def updateDatabase(i=0):
	if i == 0:
		movies = Movie.objects.all()
		for m in movies:
			try:	
				m.fetch()
				print(m, " has been updated")
			except:
				print(m, " errored. Skipped.")
				continue
	else:
		movie = Movie.objects.get(imdbid=i)
		movie.fetch()
		print(movie, " has been updated")

def createHashDatesArray(from_date, to_date, hashing_type):
	dates = [from_date]
	labels = []

	if hashing_type == "weeks":
		dt = timedelta(days=7)
		current_date = from_date
		labels.append("%s to %s" % (from_date.strftime("%d/%m/%y"), (current_date+dt).strftime("%d/%m/%y")))
		count = 1
		while current_date <= to_date:
			current_date += dt
			future_date = current_date + dt
			labels.append("%s to %s" % ((current_date + timedelta(days=1)).strftime("%d/%m/%y"), (future_date.strftime("%d/%m/%y"))))
			dates.append(current_date)
			# labels.append("Week %d" % count)
			count += 1

		labels = labels[:-1]

	elif hashing_type == "months":
		current_month = from_date.month
		current_year = from_date.year
		current_date = from_date
		while current_month != to_date.month or current_year != to_date.year:
			labels.append(current_date.strftime("%B %Y"))
			current_month = (current_month + 1) % 13
			if not current_month:
				current_year += 1
				current_month += 1

			current_date = datetime(year=current_year, month=current_month, day=1)
			dates.append(current_date)

		if current_date != to_date:
			dates.append(to_date)
			labels.append(to_date.strftime("%B %Y"))

	elif hashing_type == "years":
		current_year = from_date.year
		current_date = from_date
		while current_year != to_date.year:
			labels.append(current_date.strftime("%Y"))
			current_year += 1
			current_date = datetime(year=current_year, month=1, day=1)
			dates.append(current_date)

		if current_date != to_date:
			dates.append(to_date)
			labels.append(to_date.strftime("%Y"))



	return dates, labels

def wordcloudToUrl(wc):
	plt.clf()
	plt.imshow(wc, interpolation="bilinear")
	plt.axis("off")
	plt.margins(x=0, y=0)
	plt.tight_layout()

	wc_buffer = io.BytesIO()
	plt.savefig(wc_buffer, format='png', transparent=True)
	wc_buffer.seek(0)

	wc_data = base64.b64encode(wc_buffer.read()).decode('utf-8').replace('\n', '')
	wc_buffer.close()

	wc_url = 'data:image/png;base64,' + wc_data

	return wc_url
