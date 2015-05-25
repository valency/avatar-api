import uuid

from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
from rest_framework import viewsets
from django.core.exceptions import ObjectDoesNotExist

from settings import Settings
from serializers import *


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json;charset=utf-8'
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
    if 'taxi' in request.POST and 'src' in request.POST and 'header' in request.POST:
        traj = Trajectory(id=str(uuid.uuid4()), taxi=request.POST['taxi'])
        traj.save()
        try:
            traj.from_csv(Settings.CSV_UPLOAD_DIR + request.POST['src'], request.POST['header'].split(","))
        except IOError as e:
            return resp(500, "io error ({0}): {1}".format(e.errno, e.strerror))
        return resp(200, TrajectorySerializer(traj).data)
    else:
        return resp(500, "parameter not correct")


def get_traj_by_id(request):
    if 'id' in request.GET:
        try:
            traj = Trajectory.objects.get(id=request.GET['id'])
            return resp(200, TrajectorySerializer(traj).data)
        except ObjectDoesNotExist:
            return resp(404, "trajectory not exist")
    else:
        return resp(500, "parameter not correct")


def remove_traj_by_id(request):
    if 'id' in request.GET:
        traj = Trajectory.objects.get(id=request.GET['id'])
        traj.delete()
        return resp(200, "success")
    else:
        return resp(500, "parameter not correct")


def get_all_traj_id(request):
    return resp(200, TrajectoryListSerializer(Trajectory.objects.all(), many=True).data)
