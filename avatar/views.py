import uuid
import csv
import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status

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
    if 'src' in request.GET:
        ids = []
        traj = None
        with open(request.GET["src"]) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in sorted(reader, key=lambda d: (d['taxi'], d['t'])):
                if traj is None or row['taxi'] != traj.taxi:
                    # Create new trajectory
                    uuid_id = str(uuid.uuid4())
                    trace = Trace(id=uuid_id)
                    trace.save()
                    traj = Trajectory(id=uuid_id, taxi=row['taxi'], trace=trace)
                    traj.save()
                    ids.append(uuid_id)
                # Append current point
                sampleid = row["id"]
                p = Point(lat=float(row["lat"]), lng=float(row["lng"]))
                p.save()
                t = datetime.datetime.strptime(row["t"], "%Y-%m-%d %H:%M:%S")
                speed = int(row["speed"])
                angle = int(row["angle"])
                occupy = int(row["occupy"])
                sample = Sample(id=sampleid, p=p, t=t, speed=speed, angle=angle, occupy=occupy, src=0)
                sample.save()
                traj.trace.p.add(sample)
                traj.save()
        return Response({"ids": ids})
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
