from django.contrib import admin
from .models import *

class MovieAdmin(admin.ModelAdmin):
	list_display = ('title', 'director', 'writer', 'actors', 'released', 'created',)
	list_filter = ('title', 'director', 'writer', 'actors', 'released', 'created',)
	search_fields = ('title', 'director', 'writer', 'actors', 'released', 'created',)
	ordering = ('released', 'created',)

class WatchedMovieAdmin(admin.ModelAdmin):
	list_display = ('movie', 'viewer', 'note', 'created', 'view_date',)
	list_filter = ('movie', 'viewer', 'note', 'created','view_date',)
	ordering = ('view_date', 'created',)

admin.site.register(Movie, MovieAdmin)
admin.site.register(WatchedMovie, WatchedMovieAdmin)