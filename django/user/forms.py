from django import forms
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.utils import IntegrityError
from django.forms import EmailField, CharField

from .models import User


class SignUpForm(forms.Form):
    email = EmailField(max_length=255, required=True)
    nickname = CharField(max_length=150, strip=True, required=True)
    password = forms.CharField(
        max_length=255, min_length=6, required=True
    )
    password_confirmation = forms.CharField(
        max_length=255, min_length=6, required=True
    )

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')
        if password and password_confirmation:
            if password != password_confirmation:
                self.add_error(
                    'password_confirmation',
                    'Does not match password')
                raise forms.ValidationError("Does not match password")
        return cleaned_data

    def submit(self):
        if not self.is_valid():
            return False
        try:
            with transaction.atomic():
                cleaned_data = self.cleaned_data
                self.object = User(
                    email=cleaned_data.get('email'),
                    nickname=cleaned_data.get('nickname')
                )
                self.object.set_password(cleaned_data.get('password'))
                self.object.save()
                return True
        except IntegrityError:
            self.add_error('email', 'Already present')
            return False


class SignInForm(forms.Form):
    email = EmailField(max_length=255, required=True)
    password = CharField(
        max_length=255, min_length=6, required=True
    )

    def submit(self):
        if not self.is_valid():
            return False

        cleaned_data = self.cleaned_data
        user = authenticate(
            email=cleaned_data.get('email'),
            password=cleaned_data.get('password')
        )

        if user:
            self.object = user
            return True

        self.errors['user'] = 'Does not exist'
        return False


class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'nickname',
            'avatar'
        ]

    nickname = CharField(max_length=150, strip=True, required=True)
    avatar = forms.FileField(required=False)

    def submit(self):
        if not self.is_valid():
            return False
        try:
            cleaned_data = self.cleaned_data
            self.instance.nickname = cleaned_data.get('nickname')
            self.instance.avatar = cleaned_data.get('avatar')
            self.instance.save()
            return True
        except Exception:
            return False