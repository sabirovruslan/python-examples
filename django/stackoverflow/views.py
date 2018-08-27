from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import View

from .forms import QuestionForm, AnswerForm
from .models import Tag, Question


class QuestionCreateView(LoginRequiredMixin, View):
    login_url = '/sign_in'

    def get(self, request):
        form = QuestionForm()
        return self._render(form, request)

    def post(self, request):
        form = QuestionForm(request.POST, current_user=request.user)
        if form.submit():
            return redirect('question_detail', question_id=form.object.id)
        return self._render(form, request)

    def _render(self, form, request):
        return render(request, 'question_create.html', {'form': form})


class QuestionDetailView(View):

    def get(self, request, question_id):
        form = AnswerForm()
        question = get_object_or_404(Question, pk=question_id)
        return render(request, 'question_detail.html', {
            'question': question,
            'form': form
        })


class TagListView(View):

    def get(self, request):
        term = request.GET.get('term', '')
        tags = Tag.objects.filter(name__contains=term)
        return JsonResponse({'tags': [tag.name for tag in tags]})


class AnswerCreateView(LoginRequiredMixin, View):

    login_url = '/sign_in'

    def post(self, request, question_id=None):
        question = get_object_or_404(Question, pk=question_id)
        form = AnswerForm(
            request.POST, current_user=request.user, question=question
        )
        if form.submit():
            return redirect('question_detail', question_id=question.id)
        return render(request, 'question_detail.html', {
            'question': question,
            'form': form
        })

