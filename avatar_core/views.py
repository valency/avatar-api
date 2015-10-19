import uuid
import csv
import json
from datetime import datetime

import networkx

from django.db import IntegrityError
from django.db.models import Max, Min
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status

from celery.result import AsyncResult

from networkx.readwrite import json_graph

from serializers import *
from geometry import *

CSV_UPLOAD_DIR = "/var/www/html/avatar/data/"


class TrajectoryViewSet(viewsets.ModelViewSet):
    queryset = Trajectory.objects.all()
    serializer_class = TrajectorySerializer


class RoadViewSet(viewsets.ModelViewSet):
    queryset = Road.objects.all()
    serializer_class = RoadSerializer


@api_view(['GET'])
def demo_result(request):
    if 'id' in request.GET:
        result = AsyncResult(request.GET["id"])
        if result.ready():
            return Response({"status": result.ready(), "result": result.get()})
        else:
            return Response({"status": result.ready()})
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def demo(request):
    from tasks import heavy_task
    task = heavy_task.delay()
    return Response({"task_id": task.task_id})


@api_view(['GET'])
def add_traj_from_local_file(request):
    if 'src' in request.GET:
        try:
            ids = []
            traj = None
            with open(CSV_UPLOAD_DIR + request.GET["src"]) as csv_file:
                reader = csv.DictReader(csv_file)
                line_count = 0
                for row in sorted(reader, key=lambda d: (d['taxi'], d['t'])):
                    print "\rImporting Row: " + str(line_count),
                    line_count += 1
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
            print "Warning: road " + road.id + " has only one intersection"
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
def clear_orphan(request):
    if 'id' in request.GET:
        try:
            road_network = RoadNetwork.objects.get(id=request.GET["id"])
            removed_count = 0
            for road in road_network.roads.all():
                flag = False
                for intersection in road.intersection.all():
                    if road_network.roads.filter(intersection__id__contains=intersection.id).count() >= 2:
                        flag = True
                        break
                if not flag:
                    removed_count += 1
                    road_network.roads.remove(road)
                    print "Road: " + str(road.id) + " is removed."
            return Response({"removed": removed_count})
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
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
            # Prune points
            point_list = []
            for p in traj["trace"]["p"]:
                t = datetime.strptime(p["t"], "%Y-%m-%d %H:%M:%S").time()
                if ts <= t <= td:
                    point_list.append(p)
            # Sort by time stamp
            pruned["trace"]["p"] = sorted(point_list, key=lambda k: k['t'])
            return Response(pruned)
        else:
            # Sort by time stamp
            traj["trace"]["p"] = sorted(traj["trace"]["p"], key=lambda k: k['t'])
            return Response(traj)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def truncate_traj(request):
    if 'id' in request.GET:
        try:
            traj = Trajectory.objects.get(id=request.GET['id'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if "ts" in request.GET and "td" in request.GET:
            ts = datetime.strptime(request.GET["ts"], "%H:%M:%S").time()
            td = datetime.strptime(request.GET["td"], "%H:%M:%S").time()
            # Create new trace
            uuid_id = str(uuid.uuid4())
            trace = Trace(id=uuid_id)
            trace.save()
            for sample in traj.trace.p.all().order_by("t"):
                t = sample.t.time()
                if ts <= t <= td:
                    trace.p.add(sample)
            trace.save()
            # Create new trajectory
            truncated = Trajectory(id=uuid_id, taxi=traj.taxi, trace=trace)
            truncated.save()
            return Response(TrajectorySerializer(truncated).data)
        else:
            return Response(TrajectorySerializer(traj).data)
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
def get_road_by_id(request):
    if 'id' in request.GET:
        try:
            road = Road.objects.get(id=request.GET['id'])
            return Response(RoadSerializer(road).data)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def remove_road_network(request):
    if 'id' in request.GET:
        try:
            road_network = RoadNetwork.objects.get(id=request.GET['id'])
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


@api_view(['GET'])
def create_grid_index_by_road_network_id(request):
    if 'id' in request.GET:
        road_network = RoadNetwork.objects.get(id=request.GET["id"])
        road_network.grid_cells.clear()
        grid_count = 100
        if "grid" in request.GET:
            grid_count = int(request.GET["grid"])
        print "Finding the boundary of the road network..."
        lat_min = road_network.roads.aggregate(Min("p__lat"))["p__lat__min"]
        lat_max = road_network.roads.aggregate(Max("p__lat"))["p__lat__max"]
        lng_min = road_network.roads.aggregate(Min("p__lng"))["p__lng__min"]
        lng_max = road_network.roads.aggregate(Max("p__lng"))["p__lng__max"]
        minp = Point(lat=lat_min, lng=lng_min)
        minp.save()
        maxp = Point(lat=lat_max, lng=lng_max)
        maxp.save()
        print "Creating grid in memory..."
        grid_roads = [[[] for i in range(grid_count)] for j in range(grid_count)]
        unit_lat = (maxp.lat - minp.lat) / grid_count
        unit_lng = (maxp.lng - minp.lng) / grid_count
        for road in road_network.roads.all():
            for p in road.p.all():
                i = int((p.lat - minp.lat) / unit_lat)
                if i > grid_count - 1:
                    i = grid_count - 1
                j = int((p.lng - minp.lng) / unit_lng)
                if j > grid_count - 1:
                    j = grid_count - 1
                if road not in grid_roads[i][j]:
                    grid_roads[i][j].append(road)
        print "Saving the results..."
        for i in range(grid_count):
            for j in range(grid_count):
                rect = Rect(lat=minp.lat + unit_lat * i, lng=minp.lng + unit_lng * j, width=unit_lng, height=unit_lat)
                rect.save()
                grid = GridCell(lat_id=i, lng_id=j, area=rect)
                grid.save()
                for road in grid_roads[i][j]:
                    grid.roads.add(road)
                grid.save()
                road_network.grid_cells.add(grid)
        print "Updating the road network..."
        road_network.pmax = maxp
        road_network.pmin = minp
        road_network.grid_lat_count = grid_count
        road_network.grid_lng_count = grid_count
        road_network.save()
        return Response({
            "grid_cell_count": grid_count
        })
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_road_network_id(request):
    road_networks = []
    for road_network in RoadNetwork.objects.all():
        road_networks.append({
            "id": road_network.id,
            "city": road_network.city,
            "grid_lat_count": road_network.grid_lat_count,
            "grid_lng_count": road_network.grid_lng_count,
            "pmin": PointSerializer(road_network.pmin).data,
            "pmax": PointSerializer(road_network.pmax).data,
            "road_count": road_network.roads.count(),
            "intersection_count": road_network.intersections.count(),
            "grid_cell_count": road_network.grid_cells.count()
        })
    return Response(road_networks)


@api_view(['GET'])
def create_graph_by_road_network_id(request):
    if 'id' in request.GET:
        road_network = RoadNetwork.objects.get(id=request.GET["id"])
        graph = networkx.Graph()
        for road in road_network.roads.all():
            intersections = road.intersection.all()
            if len(intersections) >= 2:
                graph.add_edge(intersections[0].id, intersections[1].id, weight=road.length, id=road.id)
            else:
                print "WARNING: # of intersections of road " + str(road.id) + " is less than 2. This road will be ignored in the graph."
        road_network.graph = json.dumps(json_graph.node_link_data(graph))
        road_network.save()
        return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_graph_by_road_network_id(request):
    if 'id' in request.GET:
        road_network = RoadNetwork.objects.get(id=request.GET["id"])
        return Response(json.loads(road_network.graph))
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
