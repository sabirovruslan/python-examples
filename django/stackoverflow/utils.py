from django.conf import settings
from django.core.mail import send_mail


def new_answer_email_notify(request, question, answer):
    absolute_url = request.build_absolute_uri(question.get_url())
    subject = 'You get new answer for question'
    message = '{} answered to your question `{}`. You can read answer by link: {}'.format(
        answer.author.username,
        question.title,
        absolute_url
    )
    send_mail(subject, message, settings.EMAIL_HOST_USER, [question.author.email])
