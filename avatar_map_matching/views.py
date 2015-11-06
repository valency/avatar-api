from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from avatar_core.serializers import *
from hmm import *
from models import *


@api_view(['GET'])
def find_candidate_road_by_p(request):
    if 'city' in request.GET and 'lat' in request.GET and 'lng' in request.GET:
        city = RoadNetwork.objects.get(id=request.GET['city'])
        p = Point(lat=float(request.GET['lat']), lng=float(request.GET['lng']))
        dist = 500.0
        if 'dist' in request.GET:
            dist = float(request.GET['dist'])
        candidate_rids = []
        candidates = find_candidates_from_road(city, p)
        for candidate in candidates:
            if candidate["dist"] < dist:
                candidate_rids.append(candidate["rid"])
            else:
                break
        return Response(candidate_rids)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def map_matching(request):
    if 'city' in request.GET and 'id' in request.GET:
        city = RoadNetwork.objects.get(id=request.GET['city'])
        candidate_rank = 10
        if 'rank' in request.GET:
            candidate_rank = int(request.GET['rank'])
        traj = Trajectory.objects.get(id=request.GET['id'])
        hmm = HmmMapMatching()
        hmm_result = hmm.perform_map_matching(city, traj.trace, candidate_rank)
        path = hmm_result['path']
        traj.path = path
        traj.save()
        # Save the hmm path for other use
        try:
            hmm_path_result = HmmPath.objects.get(city=city, traj=traj)
            hmm_path_result.delete()
        except ObjectDoesNotExist:
            pass
        uuid_id = str(uuid.uuid4())
        new_path = Path(id=uuid_id)
        new_path.save()
        for path_fragment in path.road.all():
            new_path.road.add(path_fragment)
        new_path.save()
        hmm_path = HmmPath(city=city, traj=traj, path=new_path)
        hmm_path.save()
        # Save the emission table
        try:
            table = HmmEmissionTable.objects.get(city=city, traj=traj)
            table.delete()
        except ObjectDoesNotExist:
            pass
        candidate_2d = hmm_result['candidate_rid']
        candidate_1d = []
        for rid in candidate_2d:
            rid_list = ','.join(map(str, rid))
            candidate_1d.append(rid_list)
        candidate_rid = ';'.join(candidate_1d)
        emission_2d = hmm_result['emission_prob']
        emission_1d = []
        for prob in emission_2d:
            prob_list = ','.join(map(str, prob))
            emission_1d.append(prob_list)
        emission_prob = ';'.join(emission_1d)
        emission_table = HmmEmissionTable(city=city, traj=traj, candidate=candidate_rid, table=emission_prob)
        emission_table.save()
        # Save the transition table
        try:
            table = HmmTransitionTable.objects.get(city=city, traj=traj)
            table.delete()
        except ObjectDoesNotExist:
            pass
        transition_3d = hmm_result['transition_prob']
        transition_1d = []
        for prob in transition_3d:
            transition_2d = []
            for p in prob:
                p_list = ':'.join(map(str, p))
                transition_2d.append(p_list)
            prob_list = ','.join(transition_2d)
            transition_1d.append(prob_list)
        transition_prob = ';'.join(transition_1d)
        transition_src = transition_prob + ";" + str(hmm_result['beta'])
        transition_table = HmmTransitionTable(city=city, traj=traj, table=transition_src)
        transition_table.save()
        # Save the hmm path index
        try:
            index = HmmPathIndex.objects.get(city=city, traj=traj)
            index.delete()
        except ObjectDoesNotExist:
            pass
        path_index = hmm_result['path_index']
        path_index_src = ','.join(map(str, path_index))
        hmm_path_index = HmmPathIndex(city=city, traj=traj, index=path_index_src)
        hmm_path_index.save()
        return Response({
            "traj": TrajectorySerializer(traj).data,
            "dist": hmm_result['dist']
        })
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def reperform_map_matching(request):
    if 'city' in request.GET and 'id' in request.GET and 'pid' in request.GET and 'rid' in request.GET and 'uid' in request.GET:
        city = RoadNetwork.objects.get(id=request.GET['city'])
        candidate_rank = 10
        if 'rank' in request.GET:
            candidate_rank = int(request.GET['rank'])
        traj = Trajectory.objects.get(id=request.GET['id'])
        sample = traj.trace.p.get(id=request.GET['pid'])
        road = city.roads.get(id=request.GET['rid'])
        user = Account.objects.get(id=request.GET['uid'])
        # Insert the query pair into user action history
        try:
            action_list = UserActionHistory.objects.get(user=user, traj=traj)
            try:
                action = action_list.action.get(point=sample)
                action.delete()
            except ObjectDoesNotExist:
                pass
        except ObjectDoesNotExist:
            action_list = UserActionHistory(user=user, traj=traj)
            action_list.save()
        action = Action(point=sample, road=road)
        action.save()
        action_list.action.add(action)
        action_list.save()
        # Construct the probability tables generated by previous map matching
        candidate_str = HmmEmissionTable.objects.get(city=city, traj=traj).candidate
        emission_str = HmmEmissionTable.objects.get(city=city, traj=traj).table
        transition_str = HmmTransitionTable.objects.get(city=city, traj=traj).table
        candidate_rid = []
        emission_prob = []
        transition_prob = []
        for rid in candidate_str.split(';'):
            candidate_1d = []
            for r in rid.split(','):
                candidate_1d.append(r)
            candidate_rid.append(candidate_1d)
        for prob in emission_str.split(';'):
            emission_1d = []
            for p in prob.split(','):
                emission_1d.append(float(p))
            emission_prob.append(emission_1d)
        transition_set = transition_str.split(';')
        beta = float(transition_set[len(transition_set) - 1])
        for i in range(len(transition_set) - 1):
            transition_2d = []
            for p in transition_set[i].split(','):
                transition_1d = []
                for record in p.split(':'):
                    transition_1d.append(float(record))
                transition_2d.append(transition_1d)
            transition_prob.append(transition_2d)
        hmm = HmmMapMatching()
        hmm.candidate_rid = candidate_rid
        hmm.emission_prob = emission_prob
        hmm.transition_prob = transition_prob
        hmm_result = hmm.reperform_map_matching(city, traj.trace, candidate_rank, action_list, beta)
        path = hmm_result['path']
        traj.path = path
        traj.save()
        return Response(TrajectorySerializer(traj).data)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_candidate_rid_by_traj(request):
    if 'city' in request.GET and 'id' in request.GET:
        try:
            city = RoadNetwork.objects.get(id=request.GET['city'])
            traj = Trajectory.objects.get(id=request.GET['id'])
            candidate_str = HmmEmissionTable.objects.get(city=city, traj=traj).candidate
            candidate_rid = []
            for rids in candidate_str.split(';'):
                candidate_1d = []
                for rid in rids.split(','):
                    candidate_1d.append(rid)
                candidate_rid.append(candidate_1d)
            return Response(candidate_rid)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_emission_table_by_traj(request):
    if 'city' in request.GET and 'id' in request.GET:
        try:
            city = RoadNetwork.objects.get(id=request.GET['city'])
            traj = Trajectory.objects.get(id=request.GET['id'])
            emission_str = HmmEmissionTable.objects.get(city=city, traj=traj).table
            emission_prob = []
            for prob in emission_str.split(';'):
                emission_1d = []
                for p in prob.split(','):
                    emission_1d.append(float(p))
                emission_prob.append(emission_1d)
            return Response(emission_prob)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_transition_table_by_traj(request):
    if 'city' in request.GET and 'id' in request.GET:
        try:
            city = RoadNetwork.objects.get(id=request.GET['city'])
            traj = Trajectory.objects.get(id=request.GET['id'])
            transition_str = HmmTransitionTable.objects.get(city=city, traj=traj).table
            transition_prob = []
            transition_set = transition_str.split(';')
            beta = float(transition_set[len(transition_set) - 1])
            for i in range(len(transition_set) - 1):
                transition_2d = []
                for p in transition_set[i].split(','):
                    transition_1d = []
                    for record in p.split(':'):
                        transition_1d.append(float(record))
                    transition_2d.append(transition_1d)
                transition_prob.append(transition_2d)
            return Response({
                "beta": beta,
                "prob": transition_prob
            })
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_hmm_path_by_traj(request):
    if 'city' in request.GET and 'id' in request.GET:
        try:
            city = RoadNetwork.objects.get(id=request.GET['city'])
            traj = Trajectory.objects.get(id=request.GET['id'])
            path = HmmPath.objects.get(city=city, traj=traj).path
            return Response(PathSerializer(path).data)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_hmm_path_index_by_traj(request):
    if 'city' in request.GET and 'id' in request.GET:
        try:
            city = RoadNetwork.objects.get(id=request.GET['city'])
            traj = Trajectory.objects.get(id=request.GET['id'])
            path_index_str = HmmPathIndex.objects.get(city=city, traj=traj).index
            hmm_path_index = []
            for index in path_index_str.split(','):
                hmm_path_index.append(index)
            return Response(hmm_path_index)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_history_by_traj(request):
    if 'id' in request.GET and 'uid' in request.GET:
        try:
            traj = Trajectory.objects.get(id=request.GET['id'])
            user = Account.objects.get(id=request.GET['uid'])
            history = UserActionHistory.objects.get(user=user, traj=traj)
            action_list = []
            for action in history.action.all():
                action_list.append(action.__str__())
            return Response(action_list)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def remove_history_by_user(request):
    if 'id' in request.GET and 'uid' in request.GET:
        traj = Trajectory.objects.get(id=request.GET['id'])
        user = Account.objects.get(id=request.GET['uid'])
        history = UserActionHistory.objects.get(user=user, traj=traj)
        for action in history.action.all():
            action.delete()
        history.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
