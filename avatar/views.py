import uuid

from rest_framework.renderers import JSONRenderer
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


class RoadViewSet(viewsets.ModelViewSet):
    queryset = Road.objects.all()
    serializer_class = RoadSerializer


class IntersectionViewSet(viewsets.ModelViewSet):
    queryset = Intersection.objects.all()
    serializer_class = IntersectionSerializer


def resp(status, content):
    return JSONResponse({"status": status, "content": content})


def add_traj_from_local_file(request):
    traj = Trajectory(id=uuid.uuid4(), taxi=request.data['taxi'])
    try:
        traj.from_csv(request.data['src'], request.data['header'].split(","))
        traj.save()
    except IOError as e:
        return resp(500, "io error ({0}): {1}".format(e.errno, e.strerror))
    return resp(200, traj)




    # data = JSONParser().parse(BytesIO(request.data['traj']))
    # serializer = TrajectorySerializer(data=data)
    # if serializer.is_valid():
    #     return resp(200, serializer.validated_data)


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

#
# def index(request):
#     traj = Trajectory.objects.all()
#     serializer = TrajectorySerializer(traj, many=True)
#     return JSONResponse(serializer.data)
#     # resp = serializers.serialize("json", Trajectory.objects.all())
#     # return HttpResponse(json.dumps([{'text':o.question_text,'date':o.pub_date.strftime("%Y-%m-%d %X")} for o in Question.objects.all()]))
#     # return resp
#
#
# def find_traj_by_id(request, id):
#     # try:
#     #     obj = MyModel.objects.get(pk=id)
#     #     data = serializers.serialize('json', [obj,])
#     #     struct = json.loads(data)
#     #     data = json.dumps(struct[0])
#     #     return HttpResponse(data, mimetype='application/json')
#     # except Question.DoesNotExist:
#     #     return HttpResponse("question not exist");
#     # except:
#     return ""
#
#
