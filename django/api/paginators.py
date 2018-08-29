from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class QuestionListPagination(PageNumberPagination):
    page_size = settings.QUESTIONS_PER_PAGE
    page_size_query_param = 'page_size'
    max_page_size = 100


class AnswerListPagination(PageNumberPagination):
    page_size = settings.ANSWERS_PER_PAGE
    page_size_query_param = 'page_size'
    max_page_size = 100
