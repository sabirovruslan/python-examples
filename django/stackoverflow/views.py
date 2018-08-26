from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic.base import View

from .forms import QuestionForm
from .models import Tag


class QuestionCreateView(LoginRequiredMixin, View):
    login_url = '/sign_in'

    def get(self, request):
        form = QuestionForm()
        return self._render(form, request)

    def post(self, request):
        form = QuestionForm(request.POST, current_user=request.user)
        if form.submit():
            return redirect('question/detail')
        return self._render(form, request)

    def _render(self, form, request):
        return render(request, 'question_create.html', {'form': form})


class TagListView(View):

    def get(self, request):
        term = request.GET.get('term', '')
        tags = Tag.objects.filter(name__contains=term)
        return JsonResponse({'tags': [tag.name for tag in tags]})
