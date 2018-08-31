from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import EmailField, CharField, ImageField, DateTimeField
from django.urls import reverse


class User(AbstractBaseUser):
    email = EmailField(max_length=255, unique=True, null=False)
    nickname = CharField(max_length=150, null=False)
    avatar = ImageField()
    create_date = DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def get_url(self):
        return reverse('user:profile', kwargs={'nickname': self.username})

    def get_avatar_url(self):
        return self.avatar.url if self.avatar else staticfiles_storage.url('img/avatar.jpeg')
