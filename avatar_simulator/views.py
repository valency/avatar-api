from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from traj_generator import *
from synthetic_traj_generator import *


@api_view(['GET'])
def generate_trajectory(request):
    if "city" in request.GET and "traj" in request.GET and "point" in request.GET:
        city = RoadNetwork.objects.get(id=request.GET['city'])
        num_traj = int(request.GET['traj'])
        num_sample = int(request.GET['point'])
        stop_rate = 0.05
        sample_rate = 60
        # GPS error around 20m
        delta_lat = 0.0001
        delta_lng = 0.0002
        if "stop" in request.GET:
            stop_rate = float(request.GET['stop'])
        if "sample" in request.GET:
            sample_rate = float(request.GET['sample'])
        if "lat" in request.GET:
            delta_lat = float(request.GET['lat'])
        if "lng" in request.GET:
            delta_lng = float(request.GET['lng'])
        result = traj_generator(city, num_traj, num_sample, stop_rate, sample_rate, delta_lat, delta_lng)
        print "Finished!"
        return Response(result[1])
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def generate_synthetic_trajectory(request):
    if "city" in request.GET and "traj" in request.GET and "point" in request.GET:
        city = RoadNetwork.objects.get(id=request.GET['city'])
        num_traj = int(request.GET['traj'])
        num_sample = int(request.GET['point'])
        sample_rate = 60
        start = None
        end = None
        num_edge = 10
        shake = 0.0
        missing_rate = 0.0
        if "sample" in request.GET:
            sample_rate = float(request.GET['sample'])
        if "start" in request.GET:
            start = city.intersections.get(id=request.GET['start'])
        if "end" in request.GET:
            end = city.intersections.get(id=request.GET['end'])
        if "edge" in request.GET:
            num_edge = int(request.GET['edge'])
        if "shake" in request.GET:
            shake = float(request.GET['shake'])
        if "miss" in request.GET:
            missing_rate = float(request.GET['miss'])
        result = synthetic_traj_generator(city, num_traj, num_sample, sample_rate, start, end, num_edge, shake, missing_rate)
        traj_id = []
        for traj in result[0]:
            traj_id.append(traj.id)
        print "Finished!"
        return Response({
            "traj_id": traj_id,
            "ground_truth": result[1]
        })
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
