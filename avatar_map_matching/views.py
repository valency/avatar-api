from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from avatar_core.cache import *
from avatar_map_matching.hmm import *
from avatar_map_matching.models import *


@api_view(['GET'])
def find_candidate_road_by_p(request):
    if 'city' in request.GET and 'lat' in request.GET and 'lng' in request.GET:
        # city = RoadNetwork.objects.get(id=request.GET['city'])
        start = time.time()
        road_network = get_road_network_by_id(request.GET['city'])
        p = {"lat": float(request.GET['lat']), "lng": float(request.GET['lng'])}
        dist = 500.0
        if 'dist' in request.GET:
            dist = float(request.GET['dist'])
        candidate_rids = []
        candidates = find_candidates_from_road(road_network, p)
        if len(candidates) >= settings.AVATAR_ROAD_CANDIDATES_OF_MAP_MATCHING:
            candidates = candidates[:settings.AVATAR_ROAD_CANDIDATES_OF_MAP_MATCHING]
        for candidate in candidates:
            if candidate["dist"] < dist:
                candidate_rids.append(candidate["rid"])
            else:
                break
        end = time.time()
        log("Finding candidate roads takes " + str(end - start) + " seconds.")
        return Response(candidate_rids)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def map_matching(request):
    if 'city' in request.GET and 'id' in request.GET:
        # city = RoadNetwork.objects.get(id=request.GET['city'])
        road_network = get_road_network_by_id(request.GET['city'])
        candidate_rank = 10
        if 'rank' in request.GET:
            candidate_rank = int(request.GET['rank'])
        traj = Trajectory.objects.get(id=request.GET['id'])
        trace = TraceSerializer(traj.trace).data
        hmm = HmmMapMatching()
        start = time.time()
        hmm_result = hmm.perform_map_matching(road_network, trace, candidate_rank)
        HMM_RESULT[request.GET['id']] = hmm.generate_hmm_path(trace["id"], hmm_result)
        # path = hmm.save_hmm_path_to_database(city, trace["id"], hmm_result)
        # traj.path = path
        # traj.save()
        end = time.time()
        log("Map matching task takes " + str(end - start) + " seconds.")
        return Response({
            # "traj": TrajectorySerializer(traj).data,
            "path": HMM_RESULT[request.GET['id']],
            "emission_prob": hmm_result["emission_prob"],
            "transition_prob": hmm_result["transition_prob"],
            "path_index": hmm_result["path_index"],
            "candidate_rid": hmm_result["candidate_rid"],
            "confidence": hmm_result["confidence"],
            "dist": hmm_result['dist']
        })
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def reperform_map_matching(request):
    if 'city' in request.GET and 'id' in request.GET and 'pid' in request.GET and 'rid' in request.GET and 'uid' in request.GET:
        # city = RoadNetwork.objects.get(id=request.GET['city'])
        road_network = get_road_network_by_id(request.GET['city'])
        candidate_rank = 10
        if 'rank' in request.GET:
            candidate_rank = int(request.GET['rank'])
        pids = request.GET['pid'].split(",")
        rids = request.GET['rid'].split(",")
        if settings.DEBUG:
            log(request.GET['pid'])
            log("There are " + str(len(pids)) + " points in the query set.")
        if len(pids) != len(rids):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        traj = Trajectory.objects.get(id=request.GET['id'])
        # sample = traj.trace.p.get(id=request.GET['pid'])
        # road = city.roads.get(id=request.GET['rid'])
        # user = Account.objects.get(id=request.GET['uid'])
        # Insert the query pair into user action history
        # try:
        # action_list = UserActionHistory.objects.get(user=user, traj=traj)
        # try:
        # action = action_list.action.get(point=sample)
        # action.delete()
        # except ObjectDoesNotExist:
        # pass
        # except ObjectDoesNotExist:
        # action_list = UserActionHistory(user=user, traj=traj)
        # action_list.save()
        # action = Action(point=sample, road=road)
        # action.save()
        # action_list.action.add(action)
        # action_list.save()
        # Load road network and trace to memory
        trace = TraceSerializer(traj.trace).data
        # Convert action list to dictionary
        if not USER_HISTORY.has_key(request.GET['uid']):
            USER_HISTORY[request.GET['uid']] = dict()
        if not USER_HISTORY[request.GET['uid']].has_key(request.GET['id']):
            USER_HISTORY[request.GET['uid']][request.GET['id']] = dict()
        p_list = trace["p"]
        p_list.sort(key=lambda d: d["t"])
        for i in range(len(pids)):
            for j in range(len(p_list)):
                if p_list[j]["id"] == pids[i]:
                    USER_HISTORY[request.GET['uid']][request.GET['id']][j] = rids[i]
                    # action_set = dict()
                    # p_list = traj.trace.p.all().order_by("t")
                    # for action in action_list.action.all():
                    # for i in range(len(p_list)):
                    # if p_list[i].id == action.point.id:
                    # action_set[i] = action.road.id
        if settings.DEBUG:
            log(USER_HISTORY[request.GET['uid']][request.GET['id']])
        hmm = HmmMapMatching()
        start = time.time()
        hmm_result = hmm.reperform_map_matching(road_network, trace, candidate_rank, USER_HISTORY[request.GET['uid']][request.GET['id']])
        HMM_RESULT[request.GET['id']] = hmm.generate_hmm_path(trace["id"], hmm_result)
        # path = hmm.save_hmm_path_to_database(city, trace["id"], hmm_result)
        # traj.path = path
        # traj.save()
        end = time.time()
        log("Reperforming map matching task takes " + str(end - start) + " seconds.")
        return Response({
            "path": HMM_RESULT[request.GET['id']],
            "emission_prob": hmm_result["emission_prob"],
            "transition_prob": hmm_result["transition_prob"],
            "path_index": hmm_result["path_index"],
            "candidate_rid": hmm_result["candidate_rid"]
        })
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def save_map_matching_result(request):
    if 'city' in request.GET and 'id' in request.GET:
        city = RoadNetwork.objects.get(id=request.GET['city'])
        traj = Trajectory.objects.get(id=request.GET['id'])
        trace = TraceSerializer(traj.trace).data
        hmm = HmmMapMatching()
        path = hmm.save_hmm_path_to_database(city, trace["id"], HMM_RESULT[request.GET['id']])
        traj.path = path
        traj.save()
        # Clear cache
        HMM_RESULT.__delitem__(request.GET['id'])
        return Response(TrajectorySerializer(traj).data)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def save_user_history(request):
    if 'city' in request.GET and 'id' in request.GET and 'uid' in request.GET:
        city = RoadNetwork.objects.get(id=request.GET['city'])
        user = Account.objects.get(id=request.GET['uid'])
        traj = Trajectory.objects.get(id=request.GET['id'])
        p_list = traj.trace.p.all().order_by("t")
        if USER_HISTORY.has_key(request.GET['uid']):
            if USER_HISTORY[request.GET['uid']].has_key(request.GET['id']):
                for p_index in USER_HISTORY[request.GET['uid']][request.GET['id']]:
                    sample = traj.trace.p.get(id=p_list[p_index].id)
                    road = city.roads.get(id=USER_HISTORY[request.GET['uid']][request.GET['id']][p_index])
                    try:
                        history = UserActionHistory.objects.get(user=user, traj=traj)
                        try:
                            action = history.action.get(point=sample)
                            action.delete()
                        except ObjectDoesNotExist:
                            pass
                    except ObjectDoesNotExist:
                        history = UserActionHistory(user=user, traj=traj)
                        history.save()
                    action = Action(point=sample, road=road)
                    action.save()
                    history.action.add(action)
                    history.save()
                # Clear cache
                USER_HISTORY[request.GET['uid']].__delitem__(request.GET['id'])
        action_list = []
        for action in history.action.all():
            action_list.append(action.__str__())
        return Response(action_list)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_candidate_rid_by_traj(request):
    if 'city' in request.GET and 'id' in request.GET:
        try:
            city = RoadNetwork.objects.get(id=request.GET['city'])
            traj = Trajectory.objects.get(id=request.GET['id'])
            candidate_rid = json.loads(HmmEmissionTable.objects.get(city=city, traj=traj).candidate)
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
            emission_prob = json.loads(HmmEmissionTable.objects.get(city=city, traj=traj).table)
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
            transition_prob = json.loads(HmmTransitionTable.objects.get(city=city, traj=traj).table)
            beta = HmmTransitionTable.objects.get(city=city, traj=traj).beta
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
            hmm_path_index = json.loads(HmmPathIndex.objects.get(city=city, traj=traj).index)
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


@api_view(['GET'])
def remove_history_by_user_from_cache(request):
    if 'id' in request.GET and 'uid' in request.GET:
        if USER_HISTORY.has_key(request.GET['uid']) and USER_HISTORY[request.GET['uid']].has_key(request.GET['id']):
            USER_HISTORY[request.GET['uid']].__delitem__(request.GET['id'])
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
