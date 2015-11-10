import json
from decimal import Decimal

from networkx.readwrite import json_graph

from shortest_path import *


def find_candidates_from_road(road_network, point):
    candidates = []
    rids = []
    unit_lat = (road_network.pmax.lat - road_network.pmin.lat) / road_network.grid_lat_count
    unit_lng = (road_network.pmax.lng - road_network.pmin.lng) / road_network.grid_lng_count
    if point.lat < road_network.pmin.lat or point.lng < road_network.pmin.lng or point.lat > road_network.pmax.lat or point.lng > road_network.pmax.lng:
        print "Warning: point out of bound:", point, road_network.pmin, road_network.pmax
    else:
        lat_index = int((point.lat - road_network.pmin.lat) / unit_lat)
        lng_index = int((point.lng - road_network.pmin.lng) / unit_lng)
        for i in range(lat_index - 1 if lat_index > 0 else 0, lat_index + 2 if lat_index + 1 < road_network.grid_lat_count else road_network.grid_lat_count):
            for j in range(lng_index - 1 if lng_index > 0 else 0, lng_index + 2 if lng_index + 1 < road_network.grid_lng_count else road_network.grid_lng_count):
                grid = road_network.grid_cells.get(lat_id=i, lng_id=j)
                for road in grid.roads.all():
                    candidate = Distance.point_map_to_road(point, road)
                    candidate["rid"] = road.id
                    if road.id not in rids:
                        candidates.append(candidate)
                        rids.append(road.id)
        candidates.sort(key=lambda x: x["dist"])
    if settings.DEBUG:
        print "# of Candidates = " + str(len(candidates))
    return candidates


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

    def hmm_parameters(self, road_network, graph, trace, rank):
        deltas = []
        betas = []
        prev_p = None
        prev_candidates = None
        rank = int(rank)
        if settings.DEBUG:
            print "Setting HMM parameters..."
        count = 0
        for p in trace.p.all().order_by("t"):
            if settings.DEBUG:
                print p.id
            # Find all candidate points of each point
            candidates = find_candidates_from_road(road_network, p.p)
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
            nearest_road = road_network.roads.get(id=candidates[0]["rid"])
            deltas.append(candidates[0]["dist"])
            # Save the transition distance between each two points
            if settings.DEBUG:
                print "Saving transition distance between sample: " + str(count) + " and previous sample"
            count += 1
            if prev_p is not None:
                tran_p = []
                tran_r = []
                for c in range(rank):
                    tran_diff = []
                    tran_route = []
                    for pc in range(rank):
                        if candidates[c]["rid"] is not None and prev_candidates[pc]["rid"] is not None:
                            current_road = road_network.roads.get(id=candidates[c]["rid"])
                            prev_road = road_network.roads.get(id=prev_candidates[pc]["rid"])
                            route = ShortestPath.shortest_path_astar(road_network, graph, prev_candidates[pc]["mapped"], prev_road, candidates[c]["mapped"], current_road)
                            dist_pc = abs(Distance.earth_dist(p.p, prev_p) - route[0])
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
                prev_road = road_network.roads.get(id=prev_candidates[0]["rid"])
                beta_route = ShortestPath.shortest_path_astar(road_network, graph, candidates[0]["mapped"], nearest_road, prev_candidates[0]["mapped"], prev_road)
                beta_p = abs(Distance.earth_dist(p.p, prev_p) - beta_route[0])
                betas.append(beta_p)
            prev_p = p.p
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

    def hmm_prob_model(self, road_network, graph, trace, rank):
        # To deal with the case when the probability is too close to 0.0
        para = self.hmm_parameters(road_network, graph, trace, rank)
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

    def hmm_viterbi_backward(self, road_network, graph, trace, chosen_index):
        hmm_path_index = []
        hmm_path_rids = []
        hmm_path_dist = []
        connect_routes = []
        p_list = trace.p.all().order_by("t")
        if settings.DEBUG:
            print self.map_matching_prob
        if settings.DEBUG:
            print "Performing backward tracing..."
        final_prob = self.map_matching_prob[len(self.map_matching_prob) - 1]
        final_index = final_prob.index(max(final_prob))
        final_rid = self.candidate_rid[len(self.candidate_rid) - 1][final_index]
        if len(self.emission_dist) != 0:
            final_dist = self.emission_dist[len(self.candidate_rid) - 1][final_index]
        current_index = final_index
        hmm_path_index.append(final_index)
        hmm_path_rids.append(final_rid)
        if len(self.emission_dist) != 0:
            hmm_path_dist.append(final_dist)
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
            else:
                prev_road = road_network.roads.get(id=prev_rid)
                current_rid = self.candidate_rid[i][current_index]
                current_road = road_network.roads.get(id=current_rid)
                prev_p_map = Distance.point_map_to_road(p_list[i - 1].p, prev_road)
                current_p_map = Distance.point_map_to_road(p_list[i].p, current_road)
                connect_route = ShortestPath.shortest_path_astar(road_network, graph, prev_p_map["mapped"], prev_road, current_p_map["mapped"], current_road)
                connect_routes.append(connect_route[1])
            current_index = prev_index
        hmm_path_index.reverse()
        hmm_path_rids.reverse()
        hmm_path_dist.reverse()
        connect_routes.reverse()
        return [hmm_path_rids, connect_routes, hmm_path_dist, hmm_path_index]

    def hmm_with_label(self, road_network, graph, trace, rank, action_list, beta):
        action_set = {}
        r_index_set = {}
        p_list = trace.p.all().order_by("t")
        # Get all the (p_index, rid) pair from action_list
        for action in action_list.action.all():
            for i in range(len(p_list)):
                if p_list[i].id == action.point.id:
                    action_set[i] = action.road.id
        if settings.DEBUG:
            print action_set
        # candidate_map = []
        chosen_index = []
        ini_prob = []
        # Find the index of the candidate road for each query sample
        for p_index in action_set:
            # If the chosen road is not in the top rank list of the chosen point, replace the last candidate with the chosen road
            if action_set[p_index] not in self.candidate_rid[p_index]:
                current_road = road_network.roads.get(id=action_set[p_index])
                p_map = Distance.point_map_to_road(p_list[p_index].p, current_road)
                if p_index != 0:
                    for c in range(rank):
                        prev_road = road_network.roads.get(id=self.candidate_rid[p_index - 1][c])
                        prev_p_map = Distance.point_map_to_road(p_list[p_index - 1].p, prev_road)
                        route = ShortestPath.shortest_path_astar(road_network, graph, prev_p_map["mapped"], prev_road, p_map["mapped"], current_road)
                        tran_dist = abs(Distance.earth_dist(p_list[p_index].p, p_list[p_index - 1].p) - route[0])
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
                        next_road = road_network.roads.get(id=self.candidate_rid[p_index + 1][c])
                        next_p_map = Distance.point_map_to_road(p_list[p_index + 1].p, next_road)
                        route = ShortestPath.shortest_path_astar(road_network, graph, p_map["mapped"], current_road, next_p_map["mapped"], next_road)
                        tran_dist = abs(Distance.earth_dist(p_list[p_index].p, p_list[p_index + 1].p) - route[0])
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
        if settings.DEBUG:
            print self.emission_prob

    def perform_map_matching(self, road_network, trace, rank):
        if settings.DEBUG:
            print "Building road network graph..."
        graph = json_graph.node_link_graph(json.loads(road_network.graph))
        beta = self.hmm_prob_model(road_network, graph, trace, rank)
        if settings.DEBUG:
            print "Implementing viterbi algorithm..."
        chosen_index = self.hmm_viterbi_forward()
        sequence = self.hmm_viterbi_backward(road_network, graph, trace, chosen_index)
        hmm_path = Path(id=trace.id)
        for prev_fragment in hmm_path.road.all():
            hmm_path.road.remove(prev_fragment)
        hmm_path.save()
        ini_road = road_network.roads.get(id=sequence[0][0])
        path_fragment = PathFragment(road=ini_road)
        path_fragment.save()
        p_index = []
        for i in range(0, len(sequence[0])):
            if i > 0:
                if settings.DEBUG:
                    print sequence[0][i] == sequence[1][i - 1][-1]
            if i > 0 and len(sequence[1][i - 1]) > 1:
                path_fragment.p = ','.join(map(str, p_index))
                path_fragment.save()
                hmm_path.road.add(path_fragment)
                p_index = []
                if len(sequence[1][i - 1]) > 2:
                    for j in range(1, len(sequence[1][i - 1]) - 1):
                        next_road = road_network.roads.get(id=sequence[1][i - 1][j])
                        path_fragment = PathFragment(road=next_road)
                        path_fragment.save()
                        hmm_path.road.add(path_fragment)
                next_road = road_network.roads.get(id=sequence[0][i])
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
        return {'path': hmm_path, 'path_index': sequence[3], 'emission_prob': self.emission_prob, 'transition_prob': self.transition_prob, 'candidate_rid': self.candidate_rid, 'beta': beta, 'dist': sequence[2]}

    def reperform_map_matching(self, road_network, trace, rank, action_list, beta):
        if settings.DEBUG:
            print "Building road network graph..."
        graph = json_graph.node_link_graph(json.loads(road_network.graph))
        if settings.DEBUG:
            print "Reperform map matching with human label..."
        self.hmm_with_label(road_network, graph, trace, rank, action_list, beta)
        if settings.DEBUG:
            print "Implementing viterbi algorithm..."
        chosen_index = self.hmm_viterbi_forward()
        sequence = self.hmm_viterbi_backward(road_network, graph, trace, chosen_index)
        hmm_path = Path(id=trace.id)
        for prev_fragment in hmm_path.road.all():
            hmm_path.road.remove(prev_fragment)
        hmm_path.save()
        ini_road = road_network.roads.get(id=sequence[0][0])
        path_fragment = PathFragment(road=ini_road)
        path_fragment.save()
        p_index = []
        for i in range(0, len(sequence[0])):
            if i > 0 and len(sequence[1][i - 1]) > 1:
                path_fragment.p = ','.join(map(str, p_index))
                path_fragment.save()
                hmm_path.road.add(path_fragment)
                p_index = []
                if len(sequence[1][i - 1]) > 2:
                    for j in range(1, len(sequence[1][i - 1]) - 1):
                        next_road = road_network.roads.get(id=sequence[1][i - 1][j])
                        path_fragment = PathFragment(road=next_road)
                        path_fragment.save()
                        hmm_path.road.add(path_fragment)
                next_road = road_network.roads.get(id=sequence[0][i])
                path_fragment = PathFragment(road=next_road)
                path_fragment.save()
                # prev_id = sequence[0][i]
            p_index.append(i)
        path_fragment.p = ','.join(map(str, p_index))
        path_fragment.save()
        hmm_path.road.add(path_fragment)
        hmm_path.save()
        return {'path': hmm_path, 'mm_prob': self.map_matching_prob, 'bf_prob': self.brute_force_prob}
