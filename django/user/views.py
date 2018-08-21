from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views.generic.base import View

from .forms import SignUpForm


class SignUpView(View):

    def get(self, request):
        form = SignUpForm()
        return self._render_form(request, form)

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.submit():
            login(request, form.object)
            return redirect('profile', user_id=form.object.id)
        else:
            return self._render_form(request, form)

    def _render_form(self, request, form):
        return render(request, 'sign_up.html', {'form': form})