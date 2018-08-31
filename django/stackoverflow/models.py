from urllib.parse import urlencode

from django.db.models import CharField, Model, TextField, ForeignKey, SmallIntegerField, ManyToManyField, DateTimeField, \
    SET_NULL, CASCADE, OneToOneField, PositiveIntegerField, Manager
from django.urls import reverse


class VoteType:
    QUESTION = 'Q'
    ANSWER = 'A'

    VARIANTS = (
        (QUESTION, 'Question'),
        (ANSWER, 'Answer')
    )


class VoteMixin:
    def vote(self, user, value=False):
        try:
            vote = self.votes.get(user=user)
            if vote.vote != value:
                vote.delete()
            else:
                return False
        except Exception:
            self.votes.create(user=user, vote=value, object_id=self.id, object_type=self.get_type())
        self.rating += 1 if value else -1
        self.save()
        return True

    def get_type(self):
        raise NotImplementedError()


class QuestionManager(Manager):
    def new(self):
        return self.all().order_by('-create_date')

    def popular(self):
        return self.all().order_by('-rating', '-create_date')


class AnswerManager(Manager):
    def popular(self):
        return self.all().order_by('-rating', '-create_date')


class Question(Model):
    title = CharField(max_length=255, null=False)
    text = TextField(null=False)
    create_date = DateTimeField(auto_now_add=True)
    rating = SmallIntegerField(default=0)
    user = ForeignKey('user.User', on_delete=SET_NULL, null=True, related_name='questions')
    tags = ManyToManyField('Tag', related_name='question_tags')
    correct_answer = OneToOneField('Answer', blank=True, null=True, on_delete=CASCADE, related_name="correct_answer")

    objects = QuestionManager()

    def get_type(self):
        return VoteType.QUESTION

    @property
    def has_correct_answer(self):
        return self.correct_answer is not None

    def get_url(self):
        return reverse('stackoverflow:question', kwargs={'pk': self.pk})

    def get_vote_url(self):
        return reverse('stackoverflow:question_vote', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title


class Answer(Model):
    text = TextField(null=False)
    create_date = DateTimeField(auto_now_add=True)
    rating = SmallIntegerField(default=0)
    user = ForeignKey('user.User', null=True, related_name='answers', on_delete=SET_NULL)
    question = ForeignKey('Question', related_name="answers", on_delete=CASCADE)

    objects = AnswerManager()

    def get_type(self):
        return VoteType.ANSWER

    def mark(self, user):
        question = self.question
        if question.user != user:
            return False
        if question.has_correct_answer:
            if question.correct_answer == self:
                question.correct_answer = None
            else:
                question.correct_answer = self
        else:
            question.correct_answer = self
        question.save()
        return True

    def get_vote_url(self):
        return reverse('stackoverflow:answer_vote', kwargs={'pk': self.pk})

    def get_mark_url(self):
        return reverse('stackoverflow:answer_mark', kwargs={'pk': self.pk})


class Tag(Model):
    name = CharField(max_length=100, null=False)
    questions = ManyToManyField('Question')

    def get_url(self):
        return '{}?{}'.format(reverse('stackoverflow:search'), urlencode({'q': 'tag:' + self.name}))

    def __str__(self):
        return self.name


class Vote(Model):
    value = SmallIntegerField(null=False)
    create_date = DateTimeField(auto_now_add=True)
    user = ForeignKey('user.User', null=True, related_name='votes', on_delete=SET_NULL)
    object_id = PositiveIntegerField(null=False)
    object_type = CharField(choices=VoteType.VARIANTS, null=False, max_length=1)
