from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import CharField, Model, TextField, ForeignKey, BooleanField, \
    SmallIntegerField, ManyToManyField, DateTimeField, SET_NULL, CASCADE


class Question(Model):
    title = CharField(max_length=255, null=False)
    text = TextField(null=False)
    create_date = DateTimeField(auto_now_add=True)
    rating = SmallIntegerField(default=0)
    user = ForeignKey('user.User', on_delete=SET_NULL, null=True, related_name='questions')
    tags = ManyToManyField('Tag')


class Answer(Model):
    text = TextField(null=False)
    create_date = DateTimeField(auto_now_add=True)
    is_correct = BooleanField(null=False)
    rating = SmallIntegerField(default=0)
    user = ForeignKey('user.User', null=True, related_name='answers', on_delete=SET_NULL)


class Tag(Model):
    name = CharField(max_length=100, null=False)
    questions = ManyToManyField('Question')


class VoteQuestion(Model):
    value = SmallIntegerField(null=False)
    create_date = DateTimeField(auto_now_add=True)
    question = ForeignKey('Question', null=False, related_name='questions', on_delete=CASCADE)


class VoteAnswer(Model):
    value = SmallIntegerField(null=False)
    create_date = DateTimeField(auto_now_add=True)
    answer = ForeignKey('Answer', null=False, related_name='answers', on_delete=CASCADE)