from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import EmailField, CharField, Model, ImageField, TextField, ForeignKey, BooleanField, \
    SmallIntegerField, ManyToManyField, PositiveIntegerField, DateTimeField, SET_NULL


class User(AbstractBaseUser):
    email = EmailField(max_length=255, unique=True, null=False)
    nickname = CharField(max_length=150, null=False)
    avatar = ImageField()
    create_date = DateTimeField(auto_now_add=True)

    objects = UserManager()


class Question(Model):
    title = CharField(max_length=255, null=False)
    text = TextField(null=False)
    create_date = DateTimeField(auto_now_add=True)
    rating = SmallIntegerField(default=0)
    user = ForeignKey('User', on_delete=SET_NULL, null=True, related_name='questions')
    tags = ManyToManyField('Tag')
    votes = GenericRelation('Vote')


class Answer(Model):
    text = TextField(null=False)
    create_date = DateTimeField(auto_now_add=True)
    is_correct = BooleanField(null=False)
    rating = SmallIntegerField(default=0)
    user = ForeignKey('User', null=True, related_name='answers', on_delete=SET_NULL)
    votes = GenericRelation('Vote')


class Tag(Model):
    name = CharField(max_length=100, null=False)
    questions = ManyToManyField('Question')


class Vote(Model):
    content_type = ForeignKey(ContentType, null=True, on_delete=SET_NULL)
    object_id = PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    value = SmallIntegerField(null=False)
    create_date = DateTimeField(auto_now_add=True)
