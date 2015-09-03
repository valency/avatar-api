import uuid
import csv
from datetime import datetime

from django.db import IntegrityError

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status

from serializers import *
from common import *

CSV_UPLOAD_DIR = "/var/www/html/avatar/data/"


class TrajectoryViewSet(viewsets.ModelViewSet):
    queryset = Trajectory.objects.all()
    serializer_class = TrajectorySerializer


class RoadViewSet(viewsets.ModelViewSet):
    queryset = Road.objects.all()
    serializer_class = RoadSerializer


@api_view(['GET'])
def add_traj_from_local_file(request):
    if 'src' in request.GET:
        try:
            ids = []
            traj = None
            with open(CSV_UPLOAD_DIR + request.GET["src"]) as csv_file:
                reader = csv.DictReader(csv_file)
                for row in sorted(reader, key=lambda d: (d['taxi'], d['t'])):
                    if traj is None or row['taxi'] != traj.taxi:
                        if traj is not None:
                            # Save previous trajectory
                            traj.save()
                        # Create new trajectory
                        uuid_id = str(uuid.uuid4())
                        trace = Trace(id=uuid_id)
                        trace.save()
                        traj = Trajectory(id=uuid_id, taxi=row['taxi'], trace=trace)
                        traj.save()
                        ids.append(uuid_id)
                    # Append current point
                    sample_id = row["id"]
                    p = Point(lat=float(row["lat"]), lng=float(row["lng"]))
                    p.save()
                    t = datetime.strptime(row["t"], "%Y-%m-%d %H:%M:%S")
                    speed = int(row["speed"])
                    angle = int(row["angle"])
                    occupy = int(row["occupy"])
                    sample = Sample(id=sample_id, p=p, t=t, speed=speed, angle=angle, occupy=occupy, src=0)
                    sample.save()
                    traj.trace.p.add(sample)
            # Save the last trajectory
            traj.save()
            return Response({"ids": ids})
        except IOError:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def create_road_network_from_local_file(request):
    intersections = []

    def find_intersection_from_set(pp):
        for ii in intersections:
            if ii.p.lat == pp.lat and ii.p.lng == pp.lng:
                return ii
        ii = Intersection(id=uuid.uuid4(), p=pp)
        ii.save()
        intersections.append(ii)
        return ii

    def close_road(rr):
        # Add intersection for last point
        ii = find_intersection_from_set(rr.p.last())
        try:
            rr.intersection.add(ii)
        except IntegrityError:
            # print "Warning: road " + road.id + " has only one intersection"
            pass
        # Calculate road length
        rr.length = int(Distance.road_length(rr))
        # Save road
        rr.save()

    if 'src' in request.GET and 'city' in request.GET:
        try:
            city = request.GET["city"]
            road_network = RoadNetwork(city=city)
            road_network.save()
            with open(CSV_UPLOAD_DIR + request.GET["src"]) as csv_file:
                reader = csv.DictReader(csv_file)
                road = None
                line_count = 0
                for row in reader:
                    print "\rImporting Row: " + str(line_count),
                    line_count += 1
                    road_id = city + "-" + row["roadid"] + "-" + row["partid"]
                    p = Point(lat=float(row["lat"]), lng=float(row["lng"]))
                    p.save()
                    if road is None or road_id != road.id:
                        # Close current road if not first road
                        if road is not None:
                            close_road(road)
                        # Create new road
                        road = Road(id=road_id)
                        road.save()
                        road_network.roads.add(road)
                        # Add intersection for first point
                        intersection = find_intersection_from_set(p)
                        road.intersection.add(intersection)
                    # Append current point
                    road.p.add(p)
            # Close last road
            close_road(road)
            # Append all intersections
            for intersection in intersections:
                road_network.intersections.add(intersection)
            # Save the road network
            road_network.save()
            return Response({
                "road_network_id": road_network.id,
                "road_network_name": road_network.city,
                "road_count": road_network.roads.count(),
                "intersection_count": len(intersections)
            })
        except IOError:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_traj_by_id(request):
    if 'id' in request.GET:
        try:
            traj = Trajectory.objects.get(id=request.GET['id'])
            traj = TrajectorySerializer(traj).data
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if "ts" in request.GET and "td" in request.GET:
            ts = datetime.strptime(request.GET["ts"], "%H:%M:%S").time()
            td = datetime.strptime(request.GET["td"], "%H:%M:%S").time()
            pruned = {
                "id": traj["id"],
                "trace": {
                    "id": traj["trace"]["id"],
                    "p": []
                },
                "path": traj["path"],
                "taxi": traj["taxi"]
            }
            for p in traj["trace"]["p"]:
                t = datetime.strptime(p["t"], "%Y-%m-%d %H:%M:%S").time()
                if ts <= t <= td:
                    pruned["trace"]["p"].append(p)
            return Response(pruned)
        else:
            return Response(traj)
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
def remove_all_traj(request):
    Trajectory.objects.all().delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_all_traj_id(request):
    return Response({
        "ids": Trajectory.objects.values_list('id', flat=True).order_by('id')
    })


@api_view(['GET'])
def remove_road_network(request):
    if 'city' in request.GET:
        try:
            road_network = RoadNetwork.objects.get(city=request.GET['city'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # Delete all intersections associated with the road network
        for road in road_network.roads.all():
            road_network.roads.remove(road)
            road.delete()
        # Delete all intersections associated with the road network
        for intersection in road_network.intersections.all():
            road_network.intersections.remove(intersection)
            intersection.delete()
        road_network.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
