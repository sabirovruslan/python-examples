import datetime
import json

from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework import status

from .serializers import QuestionSerializer, AnswerSerializer
from user.models import User
from stackoverflow.models import Question, Answer, Tag


class QuestionListTest(TestCase):
    questions_data = {
        'question1': {'text': 'text1', 'rating': 3, 'days': 0},
        'question2': {'text': 'text2', 'rating': 3, 'days': 1},
        'question3': {'text': 'text3', 'rating': 2, 'days': 2},
        'question4': {'text': 'text4', 'rating': 1, 'days': 3},
        'question5': {'text': 'text5', 'rating': 0, 'days': 3},
    }

    def setUp(self):
        question_user = User.objects.create_user(
            nickname='test', email='test@eamil.com', password='top_secret'
        )

        for title, data in self.questions_data.items():
            create_date = timezone.now() + datetime.timedelta(days=data['days'])
            question = Question.objects.create(
                title=title,
                text=data['text'],
                rating=data['rating'],
                user=question_user,
            )
            question.create_date = create_date
            question.save()

    def test_get_new_questions(self):
        response = self.client.get(reverse('api:questions'))
        questions = Question.objects.all().order_by('-create_date')[:settings.QUESTIONS_PER_PAGE]
        serializer = QuestionSerializer(questions, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TrendingListTest(TestCase):
    questions_data = {
        'question1': {'text': 'text1', 'rating': 3, 'days': 0},
        'question2': {'text': 'text2', 'rating': 3, 'days': 1},
        'question3': {'text': 'text3', 'rating': 2, 'days': 2},
        'question4': {'text': 'text4', 'rating': 1, 'days': 3},
        'question5': {'text': 'text5', 'rating': 0, 'days': 3},
    }

    def setUp(self):
        question_user = User.objects.create_user(
            nickname='test', email='test@eamil.com', password='top_secret'
        )

        for title, data in self.questions_data.items():
            create_date = timezone.now() + datetime.timedelta(days=data['days'])
            question = Question.objects.create(
                title=title,
                text=data['text'],
                rating=data['rating'],
                user=question_user,
            )
            question.create_date = create_date
            question.save()

    def test_get_trending_questions(self):
        response = self.client.get(reverse('api:trending'))
        questions = Question.objects.all().order_by('-rating', '-create_date')[:settings.QUESTIONS_PER_PAGE]
        serializer = QuestionSerializer(questions, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SearchListTest(TestCase):
    questions_data = {
        'question1': {'text': 'text1', 'rating': 3, 'days': 0},
        'question12': {'text': 'text12', 'rating': 3, 'days': 1},
        'question3': {'text': 'text3', 'rating': 2, 'days': 2},
        'question4': {'text': 'text4', 'rating': 1, 'days': 3},
        'question5': {'text': 'text5', 'rating': 0, 'days': 3},
    }

    def setUp(self):
        question_user = User.objects.create_user(
            nickname='test', email='test@eamil.com', password='top_secret'
        )

        for title, data in self.questions_data.items():
            create_date = timezone.now() + datetime.timedelta(days=data['days'])
            question = Question.objects.create(
                title=title,
                text=data['text'],
                rating=data['rating'],
                user=question_user,
            )
            question.create_date = create_date
            question.save()

    def test_search_by_text(self):
        response = self.client.get(reverse('api:search') + '?q=text1')
        questions = Question.objects \
            .filter(text__icontains='text1') \
            .order_by('-rating', '-create_date')[:settings.QUESTIONS_PER_PAGE]
        serializer = QuestionSerializer(questions, many=True)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_by_title(self):
        response = self.client.get(reverse('api:search') + '?q=question1')
        questions = Question.objects \
            .filter(title__icontains='question1') \
            .order_by('-rating', '-create_date')[:settings.QUESTIONS_PER_PAGE]
        serializer = QuestionSerializer(questions, many=True)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AnswerListTest(TestCase):
    questions_data = {
        'question1': {'text': 'text1', 'rating': 3, 'days': 0},
        'question2': {'text': 'text2', 'rating': 3, 'days': 1},
        'question3': {'text': 'text3', 'rating': 2, 'days': 2},
    }

    answers_data = {
        'answer1': {'question': 'question1', 'rating': 2, 'days': 0},
        'answer2': {'question': 'question1', 'rating': 1, 'days': 1},
        'answer3': {'question': 'question2', 'rating': 2, 'days': 1},
        'answer4': {'question': 'question2', 'rating': 3, 'days': 0},
        'answer5': {'question': 'question3', 'rating': 0, 'days': 1},
        'answer6': {'question': 'question3', 'rating': 2, 'days': 0},
    }

    def setUp(self):
        question_list = {}

        question_user = User.objects.create_user(
            username='test', email='test@eamil.com', password='top_secret'
        )

        answer_user = User.objects.create_user(
            username='test2', email='test2@eamil.com', password='top_secret'
        )

        for title, data in self.questions_data.items():
            create_date = timezone.now() + datetime.timedelta(days=data['days'])
            question = Question.objects.create(
                title=title,
                text=data['text'],
                rating=data['rating'],
                user=question_user,
            )
            question.create_date = create_date
            question.save()
            question_list[title] = question

        for text, data in self.answers_data.items():
            create_date = timezone.now() + datetime.timedelta(days=data['days'])
            question = question_list[data['question']]
            answer = Answer.objects.create(
                text=text,
                rating=data['rating'],
                user=answer_user,
                question=question,
            )
            answer.create_date = create_date
            answer.save()

    def test_get_question_answers(self):
        question_id = 1
        response = self.client.get(
            reverse('api:answers', kwargs={'pk': question_id}),
            content_type='application/json'
        )
        question = Question.objects.get(pk=question_id)
        answers = question.answer_set.all().order_by('-rating', '-create_date')[:settings.ANSWERS_PER_PAGE]
        serializer = AnswerSerializer(answers, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_404_for_not_exist_question(self):
        response = self.client.get(
            reverse('api:answers', kwargs={'pk': 15}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ObtainJwtTokenTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            nickname='test', email='test@eamil.com', password='top_secret'
        )

    def test_api_token_generate(self):
        response = self.client.post(
            reverse('api:api_token_auth'),
            data=json.dumps({'nickname': 'test', 'password': 'top_secret'}),
            content_type='application/json'
        )
        self.assertRegexpMatches(response.data.get('token'), r'[^\s]+')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_existing_user_api_token_generate_failure(self):
        response = self.client.post(
            reverse('api:api_token_auth'),
            data=json.dumps({'nickname': 'test', 'password': 'incorrect_secret'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
