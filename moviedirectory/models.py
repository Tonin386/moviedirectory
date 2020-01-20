from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.core.validators import int_list_validator

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
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    username = models.CharField(max_length=16, unique=True, verbose_name="Username")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Birthdate")
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, verbose_name="Gender", null=True, blank=True)
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=50, null=True, blank=True, verbose_name="First name")
    last_name = models.CharField(max_length=50, null=True, blank=True, verbose_name="Last name")
    watched_movies = models.ManyToManyField('main.WatchedMovie', verbose_name="Watched movies", blank=True)
    followed = models.ManyToManyField('self', verbose_name="Followed persons", blank=True)
    followers = models.ManyToManyField('self', verbose_name="Followers", blank=True)

    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        ordering = ['username']

    def __str__(self):
        return self.username