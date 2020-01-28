from django.utils.translation import ugettext_lazy as _
from django_registration.forms import RegistrationForm
from .models import User
from django import forms
import datetime

class LoginForm(forms.Form):
    username = forms.CharField(label=_("Username"), max_length=16)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

class SignInForm(RegistrationForm):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field in self.fields:
    #         self.fields[field].widget.attrs.update({
    #             'class': 'form-control'
    #         })

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