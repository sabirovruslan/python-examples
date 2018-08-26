from django.conf.urls import url

from .views import QuestionCreateView, TagListView

urlpatterns = [
    url(r'^question/create', QuestionCreateView.as_view(), name='create_question'),
    url(r'^tags$', TagListView.as_view(), name='tags_list'),
]
