from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework import status

from avatar_core.serializers import *
from hmm import *


@api_view(['GET'])
def map_matching(request):
    if 'city' in request.GET and 'id' in request.GET:
        city = RoadNetwork.objects.get(id=request.GET['city'])
        candidate_rank = 10
        if 'rank' in request.GET:
            candidate_rank = int(request.GET['rank'])
        traj = Trajectory.objects.get(id=request.GET['id'])
        hmm = HmmMapMatching()
        hmm_result = hmm.perfom_map_matching(city, traj.trace, candidate_rank)
        path = hmm_result['path']
        traj.path = path
        traj.save()
        return Response(TrajectorySerializer(traj).data)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
