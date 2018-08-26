from django.conf.urls import url

from .views import SignUpView, ProfileView, SignInView, SignOutView

urlpatterns = [
    url(r'^sign_up', SignUpView.as_view(), name='sign_up'),
    url(r'^sign_in', SignInView.as_view(), name='sign_in'),
    url(r'^sign_out', SignOutView.as_view(), name='sign_out'),
    url(r'^profile', ProfileView.as_view(), name='profile'),
]
