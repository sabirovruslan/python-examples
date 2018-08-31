from django.conf.urls import url

from .views import SingUpView, LoginView, LogoutView, SettingsView, ProfileView

app_name = 'user'
urlpatterns = [
    url(r'^singup/$', SingUpView.as_view(), name='singup'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^settings/$', SettingsView.as_view(), name='settings'),
    url(r'^profile/(?P<username>[^\s]+)/?$', ProfileView.as_view(), name='profile'),
]
