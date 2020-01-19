from django.contrib import admin
from .models import *

class MovieAdmin(admin.ModelAdmin):
	list_display = ('title', 'director', 'writer', 'actors', 'released',)
	list_filter = ('title', 'director', 'writer', 'actors', 'released',)
	search_fields = ('title', 'director', 'writer', 'actors', 'released',)
	ordering = ('released',)

admin.site.register(Movie, MovieAdmin)
admin.site.register(WatchedMovie)


# Register your models here.
