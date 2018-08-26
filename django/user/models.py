from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.db.models import EmailField, CharField, ImageField, DateTimeField


class User(AbstractBaseUser):
    email = EmailField(max_length=255, unique=True, null=False)
    nickname = CharField(max_length=150, null=False)
    avatar = ImageField()
    create_date = DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
