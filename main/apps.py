from django.utils.translation import ugettext_lazy as _
from django.apps import AppConfig

class MainConfig(AppConfig):
    name = 'main'
    verbose_name = _("Movies management")
