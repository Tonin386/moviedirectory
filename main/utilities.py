from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import ugettext as _, get_language
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseNotFound, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from moviedirectory.models import *
import logging

def send_invite(asked_user, user):
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
					#Send a mail to both users
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
					#Send a mail to the user