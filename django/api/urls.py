from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from .views import QuestionList, TrendingList, SearchList, AnswerList

app_name = 'api'
urlpatterns = [
    url(r'^questions/$', QuestionList.as_view(), name='questions'),
    url(r'^trending/$', TrendingList.as_view(), name='trending'),
    url(r'^search/?$', SearchList.as_view(), name='search'),
    url(r'^questions/(?P<pk>[\d]+)/answers/$', AnswerList.as_view(), name='answers'),
    url(r'^get-token-auth/$', obtain_jwt_token, name='get_token_auth'),
]
