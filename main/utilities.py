from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from moviedirectory.models import *
import logging

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