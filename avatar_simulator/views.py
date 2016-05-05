from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from synthetic_traj_generator import *
from avatar_core.cache import *
from django.core.exceptions import ObjectDoesNotExist


@api_view(['GET'])
def generate_synthetic_trajectory(request):
    if "city" in request.GET and "traj" in request.GET and "point" in request.GET:
        road_network = get_road_network_by_id(request.GET['city'])
        num_traj = int(request.GET['traj'])
        num_sample = int(request.GET['point'])
        sample_rate = 60
        start = None
        end = None
        num_edge = num_sample
        shake = 1.0
        missing_rate = 0.0
        if "sample" in request.GET:
            sample_rate = float(request.GET['sample'])
        if "start" in request.GET:
            start = road_network["intersections"][request.GET['start']]
        if "end" in request.GET:
            end = road_network["intersections"][request.GET['end']]
        if "edge" in request.GET:
            num_edge = int(request.GET['edge'])
        if "shake" in request.GET:
            shake = float(request.GET['shake'])
        if "miss" in request.GET:
            missing_rate = float(request.GET['miss'])
        result = synthetic_traj_generator(road_network, num_traj, num_sample, sample_rate, start, end, num_edge, shake, missing_rate)
        traj_id = []
        for traj in result[0]:
            traj_id.append(traj.id)
        print "Finished!"
        return Response({
            "traj_id": traj_id,
            "ground_truth": result[1],
            "path_length": result[2]
        })
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def refactor_synthetic_trajectory(request):
    if 'id' in request.GET and 'pid' in request.GET:
        try:
            traj = Trajectory.objects.get(id=request.GET['id'])
            traj_data = TrajectorySerializer(traj).data
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        pids = request.GET['pid'].split(",")
        shake = 1.0
        if "shake" in request.GET:
            shake = float(request.GET['shake'])
        bound = 0
        if "bound" in request.GET:
            bound = int(request.GET['bound'])
        new_traj_id = synthetic_traj_refactor(traj_data, pids, shake, bound)
        new_traj = Trajectory.objects.get(id=new_traj_id)
        return Response(TrajectorySerializer(new_traj).data)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)