from django.utils.translation import ugettext_lazy as _
from django.apps import AppConfig

class UserConfig(AppConfig):
    name = 'moviedirectory'
    verbose_name = _("Members management")
