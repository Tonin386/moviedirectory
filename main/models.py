from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.core.validators import int_list_validator, MinValueValidator, MaxValueValidator
from main.api import make_request_by_id as fetch_movie

class Movie(models.Model):
	title = models.CharField(max_length=50, verbose_name="Title", null=True, blank=True)
	year = models.CharField(verbose_name="Release year", null=True, blank=True, max_length=12)
	rated = models.CharField(max_length=3, verbose_name="Rated", null=True, blank=True)
	released = models.DateField(verbose_name="Release date", null=True, blank=True)
	runtime = models.CharField(verbose_name="Runtime", max_length=255, null=True, blank=True)
	genre = models.CharField(verbose_name="Genre", max_length=255, null=True, blank=True)
	director = models.CharField(verbose_name="Director", max_length=255, null=True, blank=True)
	writer = models.TextField(verbose_name="Writer", null=True, blank=True)
	actors = models.TextField(verbose_name="Actors", null=True, blank=True)
	plot = models.TextField(verbose_name="Plot", null=True, blank=True)
	language = models.TextField(verbose_name="Language", null=True, blank=True)
	country = models.TextField(verbose_name="Country", null=True, blank=True)
	awards = models.TextField(verbose_name="Awards", null=True, blank=True)
	poster = models.CharField(verbose_name="Poster URL", max_length=255, null=True, blank=True)
	imdbid = models.CharField(verbose_name="IMDb ID", max_length=255, null=True, blank=True)
	m_type = models.CharField(verbose_name="Type", max_length=255, null=True, blank=True)
	production = models.CharField(verbose_name="Production", max_length=255, null=True, blank=True)

	def fetch(self):
		r = fetch_movie(self.imdbid, True)
		if r['Response'] == 'True' and self.imdbid:
			self.title = r['Title']
			self.year = r['Year']
			self.rated = r['Rated']

			r['Released'] = r['Released'].split(" ")
			if "Jan" in r['Released'][1]:
				r['Released'][1] = r['Released'][1].replace("Jan", "01")
			elif "Feb" in r['Released'][1]:
				r['Released'][1] = r['Released'][1].replace("Feb", "02")
			elif "Mar" in r['Released'][1]:
				r['Released'][1] = r['Released'][1].replace("Mar", "03")
			elif "Apr" in r['Released'][1]:
				r['Released'][1] = r['Released'][1].replace("Apr", "04")
			elif "May" in r['Released'][1]:
				r['Released'][1] = r['Released'][1].replace("May", "05")
			elif "Jun" in r['Released'][1]:
				r['Released'][1] = r['Released'][1].replace("Jun", "06")
			elif "Jul" in r['Released'][1]:
				r['Released'][1] = r['Released'][1].replace("Jul", "07")
			elif "Aug" in r['Released'][1]:
				r['Released'][1] = r['Released'][1].replace("Aug", "08")
			elif "Sep" in r['Released'][1]:
				r['Released'][1] = r['Released'][1].replace("Sep", "09")
			elif "Oct" in r['Released'][1]:
				r['Released'][1] = r['Released'][1].replace("Oct", "10")
			elif "Nov" in r['Released'][1]:
				r['Released'][1] = r['Released'][1].replace("Nov", "11")
			elif "Dec" in r['Released'][1]:
				r['Released'][1] = r['Released'][1].replace("Dec", "12")

			r['Released'] = r['Released'][2] + '-' + r['Released'][1] + '-' + r['Released'][0]

			self.released = r['Released']
			self.runtime = r['Runtime']
			self.genre = r['Genre']
			self.director = r['Director']
			self.writer = r['Writer']
			self.actors = r['Actors']
			self.plot = r['Plot']
			self.language = r['Language']
			self.country = r['Country']
			self.awards = r['Awards']
			self.poster = r['Poster']
			self.m_type = r['Type']

			if not "Production" in r:
				r['Production'] = "Unknown"

			self.production = r['Production']
			self.save()

	class Meta:
		verbose_name = 'Movie'
		ordering = ['title', 'year', 'released']

	def __str__(self):
		return self.title


class WatchedMovie(models.Model):
	movie = models.ForeignKey('main.Movie', verbose_name="Movie", on_delete=models.CASCADE)
	view_date = models.DateField(verbose_name="Watched on")
	note = models.IntegerField(null=True, blank=True, verbose_name="Personal note", validators=[MinValueValidator(0), MaxValueValidator(10)], default=10)
	new = models.BooleanField(verbose_name="Never seen before")
	theater = models.BooleanField(verbose_name="I saw it at theater!")
	viewer = models.ForeignKey('moviedirectory.User', verbose_name="Viewer", on_delete=models.CASCADE)
	comment = models.TextField(verbose_name="Comment", null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Watched movie"
		ordering=['view_date', 'note']

	def __str__(self):
		return self.viewer.username + " - " + self.movie.title 


# Create your models here.
