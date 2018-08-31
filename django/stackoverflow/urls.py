from django.conf.urls import url

from .views import IndexView, AskView, QuestionView, QuestionVoteView, AnswerVoteView, AnswerMarkView, SearchView

app_name = 'stackoverflow'
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^ask/$', AskView.as_view(), name='ask'),
    url(r'^question/(?P<pk>[\d]+)/?$', QuestionView.as_view(), name='question'),
    url(r'^vote/question/(?P<pk>[\d]+)/?$', QuestionVoteView.as_view(), name='question_vote'),
    url(r'^vote/answer/(?P<pk>[\d]+)/?$', AnswerVoteView.as_view(), name='answer_vote'),
    url(r'^mark/answer/(?P<pk>[\d]+)/?$', AnswerMarkView.as_view(), name='answer_mark'),
    url(r'^search/?', SearchView.as_view(), name='search'),
]
