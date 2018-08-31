from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from .models import User
from .decorators import logout_required
from .forms import UserSingUpForm, UserSettingsForm, AuthenticationByEmailForm


class SingUpView(View):
    form_class = UserSingUpForm
    template = 'sing_up.html'

    @method_decorator(logout_required(settings.PAGE_INDEX))
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template, {'form': form})

    @method_decorator(logout_required(settings.PAGE_INDEX))
    @transaction.atomic
    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.PAGE_INDEX)
        return render(request, self.template, {'form': form})


class LoginView(View):
    form_class = AuthenticationByEmailForm
    template = 'login.html'

    @method_decorator(logout_required(settings.PAGE_INDEX))
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template, {'form': form})

    @method_decorator(logout_required(settings.PAGE_INDEX))
    @transaction.atomic
    def post(self, request):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not request.POST.get('remember_me', None):
                request.session.set_expiry(0)
            login(request, user)
            return redirect(settings.PAGE_INDEX)
        return render(request, self.template, {'form': form})


class LogoutView(View):
    @method_decorator(login_required)
    def post(self, request):
        logout(request)
        return redirect(settings.PAGE_INDEX)


class SettingsView(View):
    form_class = UserSettingsForm
    template = 'edit.html'

    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        form = self.form_class(instance=request.user)
        return render(request, self.template, {'form': form, 'user': user})

    @method_decorator(login_required)
    @transaction.atomic
    def post(self, request):
        user = request.user
        form = self.form_class(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user.nickname = form.cleaned_data.get('nickname')
            avatar = form.cleaned_data.get('avatar')
            if avatar:
                user.avatar = avatar
            user.save()
            return redirect('user:settings')
        return render(request, self.template, {'form': form, 'user': user})


class ProfileView(View):
    template = 'profile.html'

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        return render(request, self.template, {'user': user})
