from django.db.models import CharField, Model, TextField, ForeignKey, SmallIntegerField, ManyToManyField, DateTimeField, \
    SET_NULL, CASCADE, OneToOneField, PositiveIntegerField


class VoteType:
    QUESTION = 'Q'
    ANSWER = 'A'

    VARIANTS = (
        (QUESTION, 'Question'),
        (ANSWER, 'Answer')
    )


class Question(Model):
    title = CharField(max_length=255, null=False)
    text = TextField(null=False)
    create_date = DateTimeField(auto_now_add=True)
    rating = SmallIntegerField(default=0)
    user = ForeignKey('user.User', on_delete=SET_NULL, null=True, related_name='questions')
    tags = ManyToManyField('Tag')
    correct_answer = OneToOneField('Answer', blank=True, null=True, on_delete=CASCADE, related_name="question_fk_1")


class Answer(Model):
    text = TextField(null=False)
    create_date = DateTimeField(auto_now_add=True)
    rating = SmallIntegerField(default=0)
    user = ForeignKey('user.User', null=True, related_name='answers', on_delete=SET_NULL)
    question = ForeignKey('Question', related_name="answers", on_delete=CASCADE)


class Tag(Model):
    name = CharField(max_length=100, null=False)
    questions = ManyToManyField('Question')


class Vote(Model):
    value = SmallIntegerField(null=False)
    create_date = DateTimeField(auto_now_add=True)
    user = ForeignKey('user.User', null=True, related_name='votes', on_delete=SET_NULL)
    object_id = PositiveIntegerField(null=False)
    object_type = CharField(choices=VoteType.VARIANTS, null=False, max_length=1)
