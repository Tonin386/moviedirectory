from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
	list_display = ('username', 'email', 'date_joined',)
	list_filter = ('username', 'email', 'is_staff', 'is_superuser', 'last_login', 'date_joined',)
	ordering = ('date_joined',)
	search_fields = ('username', 'email')

admin.site.register(User, UserAdmin)

# Register your models here.
