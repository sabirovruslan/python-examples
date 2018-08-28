from stackoverflow.models import Question

def trending_questions(reques):
    return {'trending_questions': Question.objects.all().order_by('rating')[:20]}