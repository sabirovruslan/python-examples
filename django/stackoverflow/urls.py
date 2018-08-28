from django.conf.urls import url

from .views import QuestionCreateView, TagListView, QuestionDetailView, AnswerCreateView, QuestionListView, SearchView, \
    VoteQuestionView, VoteAnswerView

urlpatterns = [
    url(r'^question/create', QuestionCreateView.as_view(), name='create_question'),
    url(r'^question/(?P<question_id>[0-9]*)$', QuestionDetailView.as_view(), name='question_detail'),
    url(r'^question/(?P<question_id>[0-9]*)/answers$', AnswerCreateView.as_view(), name='new_answer'),
    url(r'^question/search$', SearchView.as_view(), name='question_search'),
    url(r'^tags$', TagListView.as_view(), name='tags_list'),
    url(r'^vote_questions/(?P<question_id>[0-9]*)$', VoteQuestionView.as_view(), name="vote_question"),
    url(r'^vote_answer/(?P<answer_id>[0-9]*)$', VoteAnswerView.as_view(), name="vote_answer"),
    url(r'^$', QuestionListView.as_view(), name='question_list'),
]
