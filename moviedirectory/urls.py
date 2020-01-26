from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin

admin.site.site_header = "Movie Directory Administration"
admin.site.site_title = "Movie Directory"
admin.site.index_title = "Administration"

urlpatterns = [
    path('admin/', admin.site.urls, name="admin_site"),
    path('', include('main.urls')),
]
