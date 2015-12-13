from decimal import Decimal
import json

import networkx
from django.conf import settings
from networkx import NetworkXNoPath
from networkx.readwrite import json_graph

from avatar_core.geometry import *
from models import *
from django.core.cache import cache


def find_candidates_from_road(road_network, point):
    candidates = []
    rids = []
    if settings.DEBUG:
        print "Calculating the size of a unit..."
    unit_lat = (road_network["pmax"]["lat"] - road_network["pmin"]["lat"]) / road_network["grid_lat_count"]
    unit_lng = (road_network["pmax"]["lng"] - road_network["pmin"]["lng"]) / road_network["grid_lng_count"]
    if point["lat"] < road_network["pmin"]["lat"] or point["lng"] < road_network["pmin"]["lng"] or point["lat"] > road_network["pmax"]["lat"] or point["lng"] > road_network["pmax"]["lng"]:
        print "Warning: point out of bound!"
    else:
        lat_index = int((point["lat"] - road_network["pmin"]["lat"]) / unit_lat)
        lng_index = int((point["lng"] - road_network["pmin"]["lng"]) / unit_lng)
        if settings.DEBUG:
            print "The point is located in grid (" + str(lat_index) + "," + str(lng_index) + ")"
        grid = road_network["grid_cells"][str(lat_index)][str(lng_index)]
        # grid_str = cache.get("avatar_road_network_" + road_network["city"] + "_grid_cell_" + str(lat_index) + "_" + str(lng_index))
        # grid = json.loads(grid_str)
        if len(grid["roads"]) >= settings.AVATAR_ROAD_CANDIDATES_OF_MAP_MATCHING:
            for road in grid["roads"]:
                candidate = Distance.point_map_to_road(point, road)
                candidate["rid"] = road["id"]
                if road["id"] not in rids:
                    candidates.append(candidate)
                    rids.append(road["id"])
        else:
            for i in range(lat_index - 1 if lat_index > 0 else 0, lat_index + 2 if lat_index + 1 < road_network["grid_lat_count"] else road_network["grid_lat_count"]):
                for j in range(lng_index - 1 if lng_index > 0 else 0, lng_index + 2 if lng_index + 1 < road_network["grid_lng_count"] else road_network["grid_lng_count"]):
                    grid = road_network["grid_cells"][str(i)][str(j)]
                    # grid_str = cache.get("avatar_road_network_" + road_network["city"] + "_grid_cell_" + str(i) + "_" + str(j))
                    # grid = json.loads(grid_str)
                    for road in grid["roads"]:
                        candidate = Distance.point_map_to_road(point, road)
                        candidate["rid"] = road["id"]
                        if road["id"] not in rids:
                            candidates.append(candidate)
                            rids.append(road["id"])
        candidates.sort(key=lambda x: x["dist"])
    if settings.DEBUG:
        print "# of Candidates = " + str(len(candidates))
    return candidates


def find_path_from_index(graph, shortest_path_index, start, end):
    sequence = []
    if shortest_path_index is not None:
        if shortest_path_index[start["id"]].has_key(end["id"]):
            sequence = shortest_path_index[start["id"]][end["id"]]
    else:
        try:
            sequence = networkx.astar_path(graph, start["id"], end["id"])
        except NetworkXNoPath:
            pass
    if len(sequence) != 0:
        path = []
        length = 0
        for i in range(len(sequence) - 1):
            rid = graph.get_edge_data(sequence[i], sequence[i + 1])["id"]
            path.append(rid)
            length += graph.get_edge_data(sequence[i], sequence[i + 1])["weight"]
    # Two roads are not connected on the graph, set path to none
    else:
        path = None
        length = 16777215.0
    return length, path


def get_route_dist(graph, shortest_path_index, p1, road1, p2, road2):
    if road1["id"] == road2["id"]:
        dist = abs(Distance.length_to_start(p1, road1) - Distance.length_to_start(p2, road2))
        return dist, [road1["id"]]
    p_cross = Distance.check_intersection(road1, road2)
    if p_cross is not None:
        p1_cross = abs(Distance.length_to_start(p1, road1) - Distance.length_to_start(p_cross["p"], road1))
        p2_cross = abs(Distance.length_to_start(p2, road2) - Distance.length_to_start(p_cross["p"], road2))
        return p1_cross + p2_cross, [road1["id"], road2["id"]]
    else:
        # Assume the shortest path is between the closest intersections between two roads
        dist_between_sec = 16777215.0
        intersec1 = road1["intersection"]
        intersec2 = road2["intersection"]
        id1 = 0
        id2 = 0
        for i in range(len(intersec1)):
            for j in range(len(intersec2)):
                if Distance.earth_dist(intersec1[i]["p"], intersec2[j]["p"]) < dist_between_sec:
                    dist_between_sec = Distance.earth_dist(intersec1[i]["p"], intersec2[j]["p"])
                    id1 = i
                    id2 = j
        shortest_path = find_path_from_index(graph, shortest_path_index, intersec1[id1], intersec2[id2])
        if shortest_path[1] is not None:
            dist1 = abs(Distance.length_to_start(p1, road1) - Distance.length_to_start(intersec1[id1]["p"], road1))
            dist2 = abs(Distance.length_to_start(p2, road2) - Distance.length_to_start(intersec2[id2]["p"], road2))
            path = [road1["id"]] + shortest_path[1] + [road2["id"]]
            length = shortest_path[0] + dist1 + dist2
        else:
            path = shortest_path[1]
            length = shortest_path[0]
        return length, path


class HmmMapMatching:
    def __init__(self):
        self.candidate_rid = []
        self.emission_dist = []
        self.transition_dist = []
        self.transition_route = []
        self.emission_prob = []
        self.transition_prob = []
        self.map_matching_prob = []
        self.brute_force_prob = []

    def hmm_parameters(self, road_network, graph, shortest_path_index, trace, rank):
        deltas = []
        betas = []
        prev_p = None
        prev_candidates = None
        rank = int(rank)
        if settings.DEBUG:
            print "Setting HMM parameters..."
        count = 0
        # p_set = trace.p.all().order_by("t")
        p_list = trace["p"]
        p_list.sort(key=lambda d: d["t"])
        for p in p_list:
            if settings.DEBUG:
                print p["id"]
            # Find all candidate points of each point
            candidates = find_candidates_from_road(road_network, p["p"])
            # Save the emission distance and rid of each candidates
            if settings.DEBUG:
                print "Saving emission distance of sample: " + str(count)
            if len(candidates) < rank:
                if settings.DEBUG:
                    print "# of candidates is less than rank = " + str(rank) + ", now add dummy values"
                for i in range(len(candidates), rank, 1):
                    candidates.append({
                        "dist": 16777215.0,
                        "rid": None,
                        "mapped": None
                    })
            dist_p = []
            rids_p = []
            for c in range(rank):
                dist_p.append(candidates[c]["dist"])
                rids_p.append(candidates[c]["rid"])
            self.emission_dist.append(dist_p)
            self.candidate_rid.append(rids_p)
            # Save the emission distance of the nearest candidate
            nearest_road = road_network["roads"][candidates[0]["rid"]]
            deltas.append(candidates[0]["dist"])
            # Save the transition distance between each two points
            if settings.DEBUG:
                print "Saving transition distance between sample: " + str(count) + " and previous sample"
            count += 1
            if prev_p is not None:
                tran_p = []
                tran_r = []
                tran_dict = []
                for c in range(rank):
                    tran_diff = []
                    tran_route = []
                    road_dict = []
                    for pc in range(rank):
                        if candidates[c]["rid"] is not None and prev_candidates[pc]["rid"] is not None:
                            current_road = road_network["roads"][candidates[c]["rid"]]
                            prev_road = road_network["roads"][prev_candidates[pc]["rid"]]
                            route = get_route_dist(graph, shortest_path_index, prev_candidates[pc]["mapped"], prev_road, candidates[c]["mapped"], current_road)
                            dist_pc = abs(Distance.earth_dist(p["p"], prev_p) - route[0])
                        else:
                            dist_pc = 16777215.0
                            route = [[], []]
                        tran_diff.append(dist_pc)
                        tran_route.append(route[1])
                    tran_p.append(tran_diff)
                    tran_r.append(tran_route)
                self.transition_dist.append(tran_p)
                self.transition_route.append(tran_r)
                # Save the transition distance between the nearest candidates of each two points
                prev_road = road_network["roads"][prev_candidates[0]["rid"]]
                beta_route = get_route_dist(graph, shortest_path_index, candidates[0]["mapped"], nearest_road, prev_candidates[0]["mapped"], prev_road)
                beta_p = abs(Distance.earth_dist(p["p"], prev_p) - beta_route[0])
                betas.append(beta_p)
            prev_p = p["p"]
            prev_candidates = candidates
        if settings.DEBUG:
            print "Calculating delta and beta..."
        deltas.sort()
        betas.sort()
        delta = 1.4826 * deltas[len(deltas) / 2]
        if delta == 0.0:
            delta = 1.4826 * (sum(deltas) / float(len(deltas)))
        beta = betas[len(betas) / 2] / 0.69314718
        if beta == 0.0:
            beta = (sum(betas) / float(len(betas))) / 0.69314718
        return {'delta': delta, 'beta': beta}

    def hmm_prob_model(self, road_network, graph, shortest_path_index, trace, rank):
        # To deal with the case when the probability is too close to 0.0
        para = self.hmm_parameters(road_network, graph, shortest_path_index, trace, rank)
        if para['delta'] != 0.0:
            emission_para = 1.0 / (math.sqrt(2 * math.pi) * para['delta'])
        else:
            emission_para = float("Inf")
        if para['beta'] != 0.0:
            transition_para = 1.0 / para['beta']
        else:
            transition_para = float("Inf")
        if settings.DEBUG:
            print "Calculating eimission probabilities..."
        for zt in self.emission_dist:
            prob_t = []
            for xi in zt:
                exponent = -0.5 * (xi / para['delta']) * (xi / para['delta'])
                tmp_eprob = emission_para * math.exp(exponent)
                # Make sure this probability is between (0, 1)
                if tmp_eprob >= 1.0:
                    tmp_eprob = 1.0 - float(1e-16)
                if tmp_eprob <= 0.0:
                    tmp_eprob = float(1e-300)
                prob_t.append(Decimal(tmp_eprob))
            self.emission_prob.append(prob_t)
        if settings.DEBUG:
            print "Calculating transition probabilities..."
        for zt in self.transition_dist:
            prob_dt = []
            for prev_xi in zt:
                prob_x = []
                for xi in prev_xi:
                    exponent = -xi / para['beta']
                    tmp_tprob = transition_para * math.exp(exponent)
                    # Make sure this probability is between (0, 1)
                    if tmp_tprob >= 1.0:
                        tmp_tprob = 1.0 - float(1e-16)
                    if tmp_tprob <= 0.0:
                        tmp_tprob = float(1e-300)
                    prob_x.append(Decimal(tmp_tprob))
                prob_dt.append(prob_x)
            self.transition_prob.append(prob_dt)
        return para['beta']

    def hmm_viterbi_forward(self):
        chosen_index = []
        ini_prob = []
        if settings.DEBUG:
            print "Performing forward propagation..."
        for first in self.emission_prob[0]:
            ini_prob.append(Decimal(first))
        self.map_matching_prob.append(ini_prob)
        for t in range(len(self.transition_prob)):
            state_prob = []
            prev_index = []
            connect_prob = []
            for c in range(len(self.transition_prob[t])):
                candidate_prob = []
                for i in range(0, len(self.transition_prob[t][c])):
                    value = Decimal(self.map_matching_prob[t][i]) * Decimal(self.transition_prob[t][c][i]) * Decimal(self.emission_prob[t + 1][c])
                    candidate_prob.append(value)
                state_prob.append(max(candidate_prob))
                prev_index.append(candidate_prob.index(max(candidate_prob)))
                connect_prob.append(candidate_prob)
            chosen_index.append(prev_index)
            self.map_matching_prob.append(state_prob)
            self.brute_force_prob.append(connect_prob)
        return chosen_index

    def hmm_viterbi_backward(self, road_network, graph, shortest_path_index, trace, chosen_index):
        hmm_path_index = []
        hmm_path_rids = []
        hmm_path_dist = []
        connect_routes = []
        # p_list = trace.p.all().order_by("t")
        p_list = trace["p"]
        p_list.sort(key=lambda d: d["t"])
        # if settings.DEBUG:
        # print self.map_matching_prob
        if settings.DEBUG:
            print "Performing backward tracing..."
        final_prob = self.map_matching_prob[len(self.map_matching_prob) - 1]
        final_index = final_prob.index(max(final_prob))
        final_rid = self.candidate_rid[len(self.candidate_rid) - 1][final_index]
        if len(self.emission_dist) != 0:
            final_dist = self.emission_dist[len(self.candidate_rid) - 1][final_index]
            hmm_path_dist.append(final_dist)
        current_index = final_index
        hmm_path_index.append(final_index)
        hmm_path_rids.append(final_rid)
        for i in range(len(chosen_index), 0, -1):
            prev_index = chosen_index[i - 1][hmm_path_index[len(hmm_path_rids) - 1]]
            prev_rid = self.candidate_rid[i - 1][prev_index]
            hmm_path_index.append(prev_index)
            hmm_path_rids.append(prev_rid)
            if len(self.emission_dist) != 0:
                prev_dist = self.emission_dist[i - 1][prev_index]
                hmm_path_dist.append(prev_dist)
            if len(self.transition_route) != 0:
                connect_route = self.transition_route[i - 1][current_index][prev_index]
                connect_routes.append(connect_route)
            # Reperform map matching
            else:
                prev_road = road_network["roads"][prev_rid]
                current_rid = self.candidate_rid[i][current_index]
                current_road = road_network["roads"][current_rid]
                prev_p_map = Distance.point_map_to_road(p_list[i - 1]["p"], prev_road)
                current_p_map = Distance.point_map_to_road(p_list[i]["p"], current_road)
                connect_route = get_route_dist(graph, shortest_path_index, prev_p_map["mapped"], prev_road, current_p_map["mapped"], current_road)
                connect_routes.append(connect_route[1])
            current_index = prev_index
        hmm_path_index.reverse()
        hmm_path_rids.reverse()
        hmm_path_dist.reverse()
        connect_routes.reverse()
        return [hmm_path_rids, connect_routes, hmm_path_dist, hmm_path_index]

    def hmm_with_label(self, road_network, graph, shortest_path_index, trace, rank, action_set, beta):
        r_index_set = dict()
        # p_list = trace.p.all().order_by("t")
        p_list = trace["p"]
        p_list.sort(key=lambda d: d["t"])
        # Find the index of the candidate road for each query sample
        for p_index in action_set:
            # If the chosen road is not in the top rank list of the chosen point, replace the last candidate with the chosen road
            if action_set[p_index] not in self.candidate_rid[p_index]:
                current_road = road_network["roads"][action_set[p_index]]
                p_map = Distance.point_map_to_road(p_list[p_index]["p"], current_road)
                if p_index != 0:
                    for c in range(rank):
                        prev_road = road_network["roads"][self.candidate_rid[p_index - 1][c]]
                        prev_p_map = Distance.point_map_to_road(p_list[p_index - 1]["p"], prev_road)
                        route = get_route_dist(graph, shortest_path_index, prev_p_map["mapped"], prev_road, p_map["mapped"], current_road)
                        tran_dist = abs(Distance.earth_dist(p_list[p_index]["p"], p_list[p_index - 1]["p"]) - route[0])
                        tran_prob = 1.0 / beta * math.exp(-tran_dist / beta)
                        if tran_prob >= 1.0:
                            tran_prob = 1.0 - float(1e-16)
                        if tran_prob <= 0.0:
                            tran_prob = float(1e-300)
                        self.transition_prob[p_index - 1][rank - 1][c] = tran_prob
                        if settings.DEBUG:
                            print "Transition probability: " + str(tran_prob)
                if p_index != len(p_list) - 1:
                    for c in range(rank):
                        next_road = road_network["roads"][self.candidate_rid[p_index + 1][c]]
                        next_p_map = Distance.point_map_to_road(p_list[p_index + 1]["p"], next_road)
                        route = get_route_dist(graph, shortest_path_index, p_map["mapped"], current_road, next_p_map["mapped"], next_road)
                        tran_dist = abs(Distance.earth_dist(p_list[p_index]["p"], p_list[p_index + 1]["p"]) - route[0])
                        tran_prob = 1.0 / beta * math.exp(-tran_dist / beta)
                        if tran_prob >= 1.0:
                            tran_prob = 1.0 - float(1e-16)
                        if tran_prob <= 0.0:
                            tran_prob = float(1e-300)
                        self.transition_prob[p_index][rank - 1][c] = tran_prob
                        if settings.DEBUG:
                            print "Transition probability: " + str(tran_prob)
                self.candidate_rid[p_index][rank - 1] = action_set[p_index]
                r_index_set[p_index] = rank - 1
            else:
                r_index_set[p_index] = self.candidate_rid[p_index].index(action_set[p_index])
        # Refining the emission probability table with user actions
        for t in range(len(self.emission_prob)):
            for i in range(len(self.emission_prob[t])):
                if t in action_set:
                    if i == r_index_set[t]:
                        self.emission_prob[t][i] = 1.0
                    else:
                        self.emission_prob[t][i] = 0.0

    def perform_map_matching(self, road_network, trace, rank):
        if settings.DEBUG:
            print "Building road network graph..."
        graph = json_graph.node_link_graph(road_network["graph"])
        shortest_path_index = road_network["shortest_path_index"]
        beta = self.hmm_prob_model(road_network, graph, shortest_path_index, trace, rank)
        if settings.DEBUG:
            print "Implementing viterbi algorithm..."
        chosen_index = self.hmm_viterbi_forward()
        sequence = self.hmm_viterbi_backward(road_network, graph, shortest_path_index, trace, chosen_index)
        return {'path': sequence[0], 'route': sequence[1], 'dist': sequence[2], 'path_index': sequence[3], 'emission_prob': self.emission_prob, 'transition_prob': self.transition_prob}

    def reperform_map_matching(self, road_network, trace, rank, action_set):
        if settings.DEBUG:
            print "Building road network graph..."
        graph = json_graph.node_link_graph(road_network["graph"])
        shortest_path_index = road_network["shortest_path_index"]
        beta = self.hmm_prob_model(road_network, graph, shortest_path_index, trace, rank)
        if settings.DEBUG:
            print "Reperform map matching with human label..."
        self.hmm_with_label(road_network, graph, shortest_path_index, trace, rank, action_set, beta)
        if settings.DEBUG:
            print "Implementing viterbi algorithm..."
        chosen_index = self.hmm_viterbi_forward()
        sequence = self.hmm_viterbi_backward(road_network, graph, shortest_path_index, trace, chosen_index)
        return {'path': sequence[0], 'route': sequence[1]}

    def save_hmm_path_to_database(self, road_network_db, trace_id, hmm_result):
        hmm_path = Path(id=trace_id)
        for prev_fragment in hmm_path.road.all():
            hmm_path.road.remove(prev_fragment)
        hmm_path.save()
        ini_road = road_network_db.roads.get(id=hmm_result['path'][0])
        path_fragment = PathFragment(road=ini_road)
        path_fragment.save()
        p_index = []
        for i in range(len(hmm_result['path'])):
            if i > 0:
                if settings.DEBUG:
                    print hmm_result['path'][i] == hmm_result['route'][i - 1][-1]
            if i > 0 and len(hmm_result['route'][i - 1]) > 1:
                path_fragment.p = ','.join(map(str, p_index))
                path_fragment.save()
                hmm_path.road.add(path_fragment)
                p_index = []
                if len(hmm_result['route'][i - 1]) > 2:
                    for j in range(1, len(hmm_result['route'][i - 1]) - 1):
                        next_road = road_network_db.roads.get(id=hmm_result['route'][i - 1][j])
                        path_fragment = PathFragment(road=next_road)
                        path_fragment.save()
                        hmm_path.road.add(path_fragment)
                next_road = road_network_db.roads.get(id=hmm_result['path'][i])
                path_fragment = PathFragment(road=next_road)
                path_fragment.save()
                # prev_id = sequence[0][i]
            p_index.append(i)
        path_fragment.p = ','.join(map(str, p_index))
        path_fragment.save()
        hmm_path.road.add(path_fragment)
        hmm_path.save()
        for fragment in hmm_path.road.all():
            if settings.DEBUG:
                print fragment.p
            for sec in fragment.road.intersection.all():
                if settings.DEBUG:
                    print sec.id
        return hmm_path
