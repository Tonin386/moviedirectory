from datetime import datetime
from django import forms
from django_registration.forms import RegistrationForm
from django.forms import ModelForm, IntegerField
from django.core.validators import MinValueValidator, MaxValueValidator
from moviedirectory.models import User
from .models import *

class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=16)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

class SignInForm(RegistrationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'last_name',
            'first_name',
            'birth_date',
            'gender',
        ]

        widgets = {
            'birth_date': forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'date'}),
        }

    def save(self, commit=True):
        return super(SignInForm, self).save(commit=commit)

class WatchedMovieForm(forms.Form):
    user = User()
    movie = Movie()
    view_date = forms.DateField(label="Watched on")
    note = forms.IntegerField(label="Note", initial=10, validators=[MinValueValidator(0), MaxValueValidator(10)])
    new = forms.BooleanField(label="New", required=False)
    theater = forms.BooleanField(label="I saw it at theater", required=False)
    comment = forms.CharField(label="Personal comment", required=False)

    def save(self, commit=True):
        return WatchedMovie.objects.create(movie=self.movie, view_date=self.cleaned_data['view_date'], note=self.cleaned_data['note'], new=self.cleaned_data['new'], theater=self.cleaned_data['theater'], viewer=self.user, comment=self.cleaned_data['comment'])