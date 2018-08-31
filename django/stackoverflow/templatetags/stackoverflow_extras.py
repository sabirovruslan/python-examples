from datetime import timedelta

from django import template
from django.conf import settings
from django.utils import timezone
from django.utils.timesince import timesince

from stackoverflow.models import Question

register = template.Library()


@register.filter(name='startswith')
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False


@register.filter(name='get_human_date')
def get_human_date(date):
    now = timezone.now()
    difference = now - date
    if difference <= timedelta(minutes=10):
        return 'just now'
    return '%(time)s ago' % {'time': timesince(date).split(', ')[0]}


@register.inclusion_tag('snippets/question_trending_list.html')
def show_trending():
    questions = Question.objects.popular()[:settings.TRENDING_QUESTIONS_LIMIT]
    return {'questions': questions}
