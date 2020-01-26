from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import int_list_validator
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.db import models

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):

        if not username:
            raise ValueError('The given username must be set')
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):

        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('birth_date', "1970-01-01")
        extra_fields.setdefault('gender', 'M')
        extra_fields.setdefault('first_name', "User")
        extra_fields.setdefault('last_name', "Super")
        extra_fields.setdefault('email', "super@user.com")

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
    ]

    username = models.CharField(max_length=16, unique=True, verbose_name=_("Username"))
    birth_date = models.DateField(blank=True, null=True, verbose_name=_("Birthdate"))
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, verbose_name=_("Gender"), null=True, blank=True)
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    first_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("First name"))
    last_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Last name"))
    private = models.BooleanField(default=False, verbose_name=_("Private profile"))
    email_notifications = models.BooleanField(default=True, verbose_name=_("Email notification"))
    name_display = models.BooleanField(default=False, verbose_name=_("Name display"))

    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        ordering = ['username']

    def __str__(self):
        return self.username