from rest_framework import serializers
from stackoverflow.models import Question, Answer


class QuestionSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    user = serializers.ReadOnlyField(source='user.nickname')
    rating = serializers.IntegerField(read_only=True)
    create_date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', read_only=True)

    class Meta:
        model = Question
        fields = ('title', 'text', 'rating', 'create_date', 'user', 'correct_answer', 'tags')


class AnswerSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    rating = serializers.IntegerField(read_only=True)
    pub_date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', read_only=True)

    class Meta:
        model = Answer
        fields = ('text', 'rating', 'create_date', 'user')
