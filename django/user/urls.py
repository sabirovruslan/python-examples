from django.conf.urls import url

from .views import SignUpView, ProfileView, SignInView

urlpatterns = [
    url(r'^sign_up', SignUpView.as_view(), name='sign_up'),
    url(r'^sign_in', SignInView.as_view(), name='sign_in'),
    url(r'^profile/(?P<user_id>[A-Za-z0-9]*)', ProfileView.as_view(), name='profile'),
]
