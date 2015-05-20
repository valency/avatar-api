import json

from django.http import HttpResponse

from .models import Question


def index(request):
    return HttpResponse(json.dumps([{'text': o.question_text, 'date': o.pub_date.strftime("%Y-%m-%d %X")} for o in Question.objects.all()]))


def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
        return HttpResponse(json.dumps({'text': question.question_text, 'date': question.pub_date.strftime("%Y-%m-%d %X")}))
    except Question.DoesNotExist:
        return HttpResponse("question not exist");
