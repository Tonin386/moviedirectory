from django.utils.translation import ugettext_lazy as _
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin

admin.site.site_header = _("Movie Directory Administration")
admin.site.site_title = _("Movie Directory")
admin.site.index_title = _("Administration")

urlpatterns = [
    path('admin/', admin.site.urls, name="admin_site"),
    path('', include('main.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]
