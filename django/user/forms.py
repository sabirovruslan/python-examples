from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import EmailField

from .models import User
from .widgets import ClearableImageInput
from django.utils.translation import ugettext, ugettext_lazy as _


class UserSingUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('nickname', 'email', 'password1', 'password2', 'avatar',)


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('nickname', 'avatar',)

    def __init__(self, *args, **kwargs):
        super(UserSettingsForm, self).__init__(*args, **kwargs)
        self.fields['avatar'].widget = ClearableImageInput()


class AuthenticationByEmailForm(forms.Form):
    email = EmailField(max_length=255, required=True)
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(email)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(AuthenticationByEmailForm, self).__init__(*args, **kwargs)

        self.username_field = User._meta.get_field(User.USERNAME_FIELD)
        if self.fields['email'].label is None:
            self.fields['email'].label = 'Email'

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'email': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache