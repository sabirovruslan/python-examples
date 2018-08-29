from django.conf import settings
from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from stackoverflow.models import Question

from .paginators import QuestionListPagination, AnswerListPagination
from .serializers import QuestionSerializer, AnswerSerializer


class QuestionList(ListAPIView):
    serializer_class = QuestionSerializer
    model = serializer_class.Meta.model
    pagination_class = QuestionListPagination

    def get_queryset(self):
        return self.model.objects.new()


class TrendingList(ListAPIView):
    serializer_class = QuestionSerializer
    model = serializer_class.Meta.model

    def get_queryset(self):
        return self.model.objects.popular()[:settings.QUESTIONS_PER_PAGE]


class SearchList(QuestionList):
    def get_queryset(self):
        search_query = self.request.GET.get('q')[:255]
        if not search_query:
            return Question.objects.none()
        query = Q(title__icontains=search_query) | Q(text__icontains=search_query)
        return Question.objects.filter(query).order_by('-rating', '-create_date')


class AnswerList(ListAPIView):
    serializer_class = AnswerSerializer
    model = serializer_class.Meta.model
    pagination_class = AnswerListPagination

    def get_queryset(self):
        try:
            question = Question.objects.get(id=self.kwargs.get('pk'))
        except Question.DoesNotExist:
            raise NotFound()
        return question.answer_set.popular()
