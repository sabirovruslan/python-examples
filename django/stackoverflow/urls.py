from django.conf.urls import url

from .views import QuestionCreateView, TagListView, QuestionDetailView

urlpatterns = [
    url(r'^question/create', QuestionCreateView.as_view(), name='create_question'),
    url(r'^question/<int:question_id>$', QuestionDetailView.as_view(), name='question_detail'),
    url(r'^tags$', TagListView.as_view(), name='tags_list'),
]
