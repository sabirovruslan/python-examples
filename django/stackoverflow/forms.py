from django import forms
from django.db import transaction

from .models import Question, Tag


class QuestionForm(forms.Form):
    title = forms.CharField(max_length=255, strip=True, required=True)
    text = forms.CharField(strip=True, required=True)
    user_id = forms.fields.IntegerField(required=False)
    tags = []

    def __init__(self, data=None, **kwargs):
        if data:
            self.tags = data.get('tags', None)
        if self.tags:
            self.tags = [item for item in self.tags.split(',')]
        self.current_user = kwargs.pop('current_user', None)
        super(QuestionForm, self).__init__(data, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data
        if not self.current_user:
            raise forms.ValidationError('user_id is not present')

        if not self.tags:
            raise forms.ValidationError('tags are not present')
        cleaned_data['user_id'] = self.current_user.id
        cleaned_data['tags'] = self.tags
        return cleaned_data

    def submit(self):
        if not self.is_valid():
            return False

        try:
            with transaction.atomic():
                params = {'title': self.cleaned_data['title'], 'text': self.cleaned_data['text'],
                          'user_id': self.cleaned_data['user_id']}
                self.object = Question.objects.create(**params)
                self.object.tags.set(self._tags_ids())
                return True
        except Exception as e:
            return False

    def _tags_ids(self):
        tags = []
        for item in self.tags:
            tag, _ = Tag.objects.get_or_create(name=item)
            tags.append(tag.id)
        return tags
