import urllib

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.views import View

from .utils import new_answer_email_notify
from .forms import QuestionAskForm, AnswerForm
from .models import Question, Answer, Tag


class PaginationMixin(object):
    def paginate(self, request, items_per_page=settings.QUESTIONS_PER_PAGE, pagination_limit=100):
        try:
            limit = int(request.GET.get('limit', items_per_page))
        except ValueError:
            limit = items_per_page
        if limit > pagination_limit:
            limit = items_per_page
        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            raise Http404
        paginator = Paginator(self.get_query_set(), limit)
        get_params = request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if len(get_params) > 0:
            paginator.url = '{}?{}&page='.format(self.get_url(), urlencode(get_params.items()))
        else:
            paginator.url = '{}?page='.format(self.get_url())
        try:
            page = paginator.page(page)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        return paginator, page


class IndexView(PaginationMixin, View):
    template = 'question_list.html'

    def get(self, request):
        paginator, page = self.paginate(request, settings.QUESTIONS_PER_PAGE)
        return render(request, self.template, {
            'questions': page.object_list,
            'paginator': paginator,
            'page': page,
        })

    def get_query_set(self):
        return Question.objects.popular() if self.request.GET.get('sort') else Question.objects.new()

    def get_url(self):
        return reverse('stackoverflow:index')


class SearchView(PaginationMixin, View):
    template = 'question_search.html'
    search_query = None

    def get(self, request):
        self.search_query = request.GET.get('q')[:255]
        paginator, page = self.paginate(request, settings.QUESTIONS_PER_PAGE)
        return render(request, self.template, {
            'questions': page.object_list,
            'paginator': paginator,
            'page': page,
        })

    def get_query_set(self):
        if not self.search_query:
            return Question.objects.none()
        if self.search_query.startswith('tag:'):
            try:
                tag = get_object_or_404(Tag, name=self.search_query[len('tag:'):])
            except Http404:
                return Question.objects.none()
            return tag.question_tags.popular()
        query = Q(title__icontains=self.search_query) | Q(text__icontains=self.search_query)
        return Question.objects.filter(query).order_by('-rating', '-create_date')

    def get_url(self):
        return reverse('stackoverflow:search')


class QuestionView(PaginationMixin, View):
    form_class = AnswerForm
    template = 'question_detail.html'
    question = None
    form = None

    def do_response(self, request):
        paginator, page = self.paginate(request, settings.ANSWERS_PER_PAGE)
        return render(request, self.template, {
            'question': self.question,
            'form': self.form,
            'answers': page.object_list,
            'paginator': paginator,
            'page': page,
        })

    def get(self, request, pk):
        self.form = self.form_class(None)
        self.question = get_object_or_404(Question, pk=pk)
        return self.do_response(request)

    @method_decorator(login_required)
    @transaction.atomic
    def post(self, request, pk):
        self.form = self.form_class(request.POST)
        self.question = get_object_or_404(Question, pk=pk)
        if self.form.is_valid():
            answer = self.form.save(commit=False)
            answer.complete_and_save(question=self.question, user=request.user)
            new_answer_email_notify(request, self.question, answer)
            return redirect(self.get_url())
        return self.do_response(request)

    def get_query_set(self):
        return self.question.answer_set.popular()

    def get_url(self):
        return self.question.get_url()


class AskView(View):
    form_class = QuestionAskForm
    template = 'question_form.html'

    @method_decorator(login_required)
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template, {'form': form})

    @method_decorator(login_required)
    @transaction.atomic
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            tags = form.cleaned_data['tags']
            question.complete_and_save(tags=tags, user=request.user)
            return redirect(question.get_url())
        return render(request, self.template, {'form': form})


class AnswerMarkView(View):
    @transaction.atomic
    def post(self, request, pk):
        if request.user.is_authenticated():
            answer = get_object_or_404(Answer, pk=pk)
            return JsonResponse({'success': answer.mark(request.user)})
        else:
            return HttpResponseForbidden()


class VoteView(View):
    @transaction.atomic
    def post(self, request, pk):
        if request.user.is_authenticated():
            value = True if request.POST.get('value') == 'true' else False
            entity = get_object_or_404(self.get_model(), pk=pk)
            entity.vote(request.user, value)
            return JsonResponse({'rating': entity.rating})
        else:
            return HttpResponseForbidden()

    def get_model(self):
        raise NotImplementedError()


class QuestionVoteView(VoteView):
    def get_model(self):
        return Question


class AnswerVoteView(VoteView):
    def get_model(self):
        return Answer
