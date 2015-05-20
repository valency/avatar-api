import json
import uuid

from django.core import serializers

from django.http import HttpResponse

from capsule import Capsule
from models import *


def index(request):
    resp = serializers.serialize("json", Trajectory.objects.all())
    # return HttpResponse(json.dumps([{'text':o.question_text,'date':o.pub_date.strftime("%Y-%m-%d %X")} for o in Question.objects.all()]))
    return resp


def find_traj_by_id(request, id):
    # try:
    #     obj = MyModel.objects.get(pk=id)
    #     data = serializers.serialize('json', [obj,])
    #     struct = json.loads(data)
    #     data = json.dumps(struct[0])
    #     return HttpResponse(data, mimetype='application/json')
    # except Question.DoesNotExist:
    #     return HttpResponse("question not exist");
    # except:
    return ""


def create_traj(request):
    try:
        src = json.loads(request.POST['traj'])
        trace = Trace(id=uuid.uuid4())
        for p in src["trace"]["p"]:
            point = Point(lat=p["p"]["lat"], lng=p["p"]["lng"])
            sample = Sample(id=p["id"], p=point, t=p["t"], speed=p["speed"], angle=p["angle"], occupy=p["occupy"], meta=p["meta"], src=p["src"])
            trace.p.add(sample)
        traj = Trajectory(id=uuid.uuid4(), taxi=src["taxi"], trace=trace)
        traj.save()

    except TypeError:
        return HttpResponse(Capsule.tojson(500, "parse error"), mimetype="application/json")
