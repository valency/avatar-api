from rest_framework.renderers import JSONRenderer
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
from rest_framework import viewsets

from serializers import *


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class TrajectoryViewSet(viewsets.ModelViewSet):
    queryset = Trajectory.objects.all()
    serializer_class = TrajectorySerializer


def index(request):
    traj = Trajectory.objects.all()
    serializer = TrajectorySerializer(traj, many=True)
    return JSONResponse(serializer.data)
    # resp = serializers.serialize("json", Trajectory.objects.all())
    # return HttpResponse(json.dumps([{'text':o.question_text,'date':o.pub_date.strftime("%Y-%m-%d %X")} for o in Question.objects.all()]))
    # return resp


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
    data = JSONParser().parse(BytesIO(request.data['traj']))
    serializer = TrajectorySerializer(data=data)
    if serializer.is_valid():
        return JSONResponse({"status": 200, "content": serializer.validated_data})


        # try:
        #     src = json.loads(request.POST['traj'])
        #     trace = Trace(id=uuid.uuid4())
        #     for p in src["trace"]["p"]:
        #         point = Point(lat=p["p"]["lat"], lng=p["p"]["lng"])
        #         sample = Sample(id=p["id"], p=point, t=p["t"], speed=p["speed"], angle=p["angle"], occupy=p["occupy"], meta=p["meta"], src=p["src"])
        #         trace.p.add(sample)
        #     traj = Trajectory(id=uuid.uuid4(), taxi=src["taxi"], trace=trace)
        #     traj.save()
        #
        # except TypeError:
        #     return HttpResponse(Capsule.tojson(500, "parse error"), mimetype="application/json")
