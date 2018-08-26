from django.contrib.auth import login
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic.base import View

from .models import User
from .forms import SignUpForm, SignInForm


class SignUpView(View):

    def get(self, request):
        form = SignUpForm()
        return self._render(request, form)

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.submit():
            login(request, form.object)
            return redirect('profile', user_id=form.object.id)
        else:
            return self._render(request, form)

    def _render(self, request, form):
        return render(request, 'sign_up.html', {'form': form})


class ProfileView(View):

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        return render(request, 'profile.html', {'user_data': user})


class SignInView(View):

    def get(self, request):
        form = SignInForm()
        return self._render(request, form)

    def post(self, request):
        form = SignInForm(request.POST)
        if form.submit():
            login(request, form.object)
            return redirect('profile', user_id=form.object.id)
        else:
            return self._render(request, form)

    def _render(self, request, form):
        return render(request, 'sign_in.html', {'form': form})
