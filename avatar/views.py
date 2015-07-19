import uuid

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status

from settings import Settings
from serializers import *


class TrajectoryViewSet(viewsets.ModelViewSet):
    queryset = Trajectory.objects.all()
    serializer_class = TrajectorySerializer


class RoadViewSet(viewsets.ModelViewSet):
    queryset = Road.objects.all()
    serializer_class = RoadSerializer


class IntersectionViewSet(viewsets.ModelViewSet):
    queryset = Intersection.objects.all()
    serializer_class = IntersectionSerializer


@api_view(['GET'])
def add_traj_from_local_file(request):
    if 'taxi' in request.GET and 'src' in request.GET and 'header' in request.GET:
        traj = Trajectory(id=str(uuid.uuid4()), taxi=request.GET['taxi'])
        traj.save()
        try:
            traj.from_csv(Settings.CSV_UPLOAD_DIR + request.GET['src'], request.GET['taxi'], request.GET['header'].split(","))
        except IOError:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(TrajectorySerializer(traj).data)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_traj_by_id(request):
    if 'id' in request.GET:
        try:
            traj = Trajectory.objects.get(id=request.GET['id'])
            return Response(TrajectorySerializer(traj).data)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def remove_traj_by_id(request):
    if 'id' in request.GET:
        traj = Trajectory.objects.get(id=request.GET['id'])
        traj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_traj_id(request):
    return Response({
        "ids": Trajectory.objects.values_list('id', flat=True).order_by('id')
    })
