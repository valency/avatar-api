from common import *
from shortest_path import *


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

    def hmm_parameters(self, road_network, trace, rank):
        deltas = []
        betas = []
        prev_p = None
        prev_candidates = None
        #        prev_road = None
        rank = int(rank)
        print "Setting HMM parameters..."
        print "Before setting HMM parameters: size of transition_prob is " + str(len(self.transition_prob))
        count = 0
        for p in trace.p.all():
            # find all candidate points of each point
            candidates = find_candidates_from_road(road_network, p.p)
            # save the emission distance and rid of each candidates
            print "\rSaving emission distance of sample: " + str(count)
            dist_p = []
            rids_p = []
            for c in range(rank):
                dist_p.append(candidates[c]["dist"])
                rids_p.append(candidates[c]["rid"])
            self.emission_dist.append(dist_p)
            self.candidate_rid.append(rids_p)
            # save the emission distance of the nearest candidate
            nearest_road = road_network.roads.get(id=candidates[0]["rid"])
            deltas.append(candidates[0]["dist"])
            # save the transition distance between each two points
            print "\rSaving transition distance between sample: " + str(count) + " and previous sample",
            count += 1
            if prev_p is not None:
                tran_p = []
                tran_r = []
                for c in range(rank):
                    tran_diff = []
                    tran_route = []
                    for pc in range(rank):
                        current_road = road_network.roads.get(id=candidates[c]["rid"])
                        prev_road = road_network.roads.get(id=prev_candidates[pc]["rid"])
                        #                        route = ShortestPath.shortest_path_astar(road_network, candidates[c]["mapped"], current_road, prev_candidates[pc]["mapped"], prev_road)
                        route = ShortestPath.shortest_path_astar(road_network, prev_candidates[pc]["mapped"], prev_road, candidates[c]["mapped"], current_road)
                        dist_pc = abs(Distance.earth_dist(p.p, prev_p) - route[0])
                        #                        dist_pc = abs(Distance.earth_dist(p.p, prev_p))
                        tran_diff.append(dist_pc)
                        tran_route.append(route[1])
                    tran_p.append(tran_diff)
                    tran_r.append(tran_route)
                self.transition_dist.append(tran_p)
                self.transition_route.append(tran_r)
                # save the transition distance between the nearest candidates of each two points
                prev_road = road_network.roads.get(id=prev_candidates[0]["rid"])
                beta_route = ShortestPath.shortest_path_astar(road_network, candidates[0]["mapped"], nearest_road, prev_candidates[0]["mapped"], prev_road)
                beta_p = abs(Distance.earth_dist(p.p, prev_p) - beta_route[0])
                #		print str(p.p.lat) + "," + str(p.p.lng) + ";" + str(prev_p.lat) + "," + str(prev_p.lng)
                #                beta_p = abs(Distance.earth_dist(p.p, prev_p))
                betas.append(beta_p)
            prev_p = p.p
            prev_candidates = candidates
        #            prev_road = nearest_road
	print "After setting HMM parameters: size of transition_prob is " + str(len(self.transition_prob))
        print "Calculating delta and beta..."
        deltas.sort()
        betas.sort()
        delta = 1.4826 * deltas[len(deltas) / 2]
        beta = betas[len(betas) / 2] / 0.69314718
        return {'delta': delta, 'beta': beta}

    def hmm_prob_model(self, road_network, trace, rank):
        para = self.hmm_parameters(road_network, trace, rank)
        emission_para = 1.0 / (math.sqrt(2 * math.pi) * para['delta'])
        transition_para = 1.0 / para['beta']

        print "Calculating eimission probabilities..."
        for zt in self.emission_dist:
            prob_t = []
            for xi in zt:
                exponent = -0.5 * (xi / para['delta']) * (xi / para['delta'])
                prob_t.append(emission_para * math.exp(exponent))
            self.emission_prob.append(prob_t)
        print "Calculating transition probabilities..."
        print "Before calculating HMM model: size of transition_prob is " + str(len(self.transition_prob))
	print "Size of transition_dist is " + str(len(self.transition_dist))
        for zt in self.transition_dist:
            prob_dt = []
            for prev_xi in zt:
                prob_x = []
                for xi in prev_xi:
                    exponent = -xi / para['beta']
                    prob_x.append(transition_para * math.exp(exponent))
                prob_dt.append(prob_x)
            self.transition_prob.append(prob_dt)
        print "After calculating HMM model: size of transition_prob is " + str(len(self.transition_prob))

    def hmm_viterbi_forward(self):
        chosen_index = []
        ini_prob = []
        print "Performing forward propagation..."
        for first in self.emission_prob[0]:
            ini_prob.append(first)
            # Pretending there are num(rank) of previous candidate points pointing to each starting candidate points
            # brute_force_ini_prob = []
        #            for i in range(0, len(first)):
        #                brute_force_ini_prob.append(first)
        self.map_matching_prob.append(ini_prob)
        #        self.brute_force_prob.append(brute_force_ini_prob)
        # print len(self.transition_prob)
        # print len(self.transition_prob[0])
        # print len(self.transition_prob[0][0])
        for t in range(0, len(self.transition_prob)):
            state_prob = []
            prev_index = []
            connect_prob = []
            for current in self.transition_prob[t]:
                candidate_prob = []
                for i in range(0, len(current)):
                    value = self.map_matching_prob[t][i] * current[i] * self.emission_prob[t + 1][i]
                    candidate_prob.append(value)
                state_prob.append(max(candidate_prob))
                prev_index.append(candidate_prob.index(max(candidate_prob)))
                connect_prob.append(candidate_prob)
            chosen_index.append(prev_index)
            self.map_matching_prob.append(state_prob)
            self.brute_force_prob.append(connect_prob)
        #	print len(self.transition_dist)
        #	print len(self.transition_prob)
        #	print len(self.transition_route)
        #	print len(chosen_index)
        return chosen_index

    def hmm_viterbi_backward(self, chosen_index):
        hmm_path_index = []
        hmm_path_rids = []
        connect_routes = []
        # print len(chosen_index)
        # print len(self.candidate_rid)
        # print len(self.candidate_rid[0])
        print "Performing backward tracing..."
        final_prob = self.map_matching_prob[len(self.map_matching_prob) - 1]
        final_index = final_prob.index(max(final_prob))
        final_rid = self.candidate_rid[len(self.candidate_rid) - 1][final_index]
        current_index = final_index
        hmm_path_index.append(final_index)
        hmm_path_rids.append(final_rid)
        print "After viterbi forward: size of chosen_index is " + str(len(chosen_index))
        for i in range(len(chosen_index), 0, -1):
            prev_index = chosen_index[i - 1][hmm_path_index[len(hmm_path_rids) - 1]]
            # print len(self.candidate_rid)
            # print len(self.candidate_rid[i-1])
            print prev_index
            connect_route = self.transition_route[i - 1][current_index][prev_index]
            print self.transition_route[i - 1][current_index]
            prev_rid = self.candidate_rid[i - 1][prev_index]
            print prev_rid
            # print p_c_route
            hmm_path_index.append(prev_index)
            hmm_path_rids.append(prev_rid)
            connect_routes.append(connect_route)
            current_index = prev_index
        # print len(hmm_path_rids)
        hmm_path_rids.reverse()
        connect_routes.reverse()
        return [hmm_path_rids, connect_routes]

    def perfom_map_matching(self, road_network, trace, rank):
        print "Beginning: size of transition_prob is " + str(len(self.transition_prob))
        self.hmm_prob_model(road_network, trace, rank)
        print "Implementing viterbi algorithm..."
        chosen_index = self.hmm_viterbi_forward()
        print "After viterbi: size of transition_prob is " + str(len(self.transition_prob))
        sequence = self.hmm_viterbi_backward(chosen_index)
        hmm_path = Path(id=trace.id)
        for prev_fragment in hmm_path.road.all():
            hmm_path.road.remove(prev_fragment)
        hmm_path.save()
        ini_road = road_network.roads.get(id=sequence[0][0])
        path_fragment = PathFragment(road=ini_road)
        path_fragment.save()
        p_index = []
        print sequence[0]
        for i in range(0, len(sequence[0])):
            if i > 0:
                print sequence[1][i - 1]
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
                prev_id = sequence[0][i]
            p_index.append(i)
        path_fragment.p = ','.join(map(str, p_index))
        path_fragment.save()
        hmm_path.road.add(path_fragment)
        hmm_path.save()
        for fragment in hmm_path.road.all():
            print fragment.p
            for sec in fragment.road.intersection.all():
                print sec.id
        return {'path': hmm_path, 'mm_prob': self.map_matching_prob, 'bf_prob': self.brute_force_prob}

# def reperform_map_matching(self, road_network, trace, prob, rank, diff):
#        print "Combining user's preference..."
#        # Assuming the structure of diff is: [[point_index_from_trace, road_id], [...], ...]
#        self.map_matching_prob = prob
#        for chosen in diff:
#            p = trace.p.all()[chosen[0]]
#            candidates = find_candidates_from_road(road_network, p.p)
#            for c in range(0, len(candidates)):
#                if candidates[c]["rid"] == chosen[1]:
#                    if c >= rank:
#                        print "The chosen road mapped to point " + str(chosen[0]) + " is not in the top " + str(rank) + " candidates!"
#                    else:
#                        for i in range(rank):
#                            if i == c:
#                                self.map_matching_prob[chosen[0]][c] = 1.0
#                            else:
#                                self.map_matching_prob[chosen[0]][c] = 0.0
#                break
#        print "Implementing viterbi algorithm..."
#        sequence = self.hmm_viterbi_backward([])
#        hmm_path = Path(id=trace.id)
#        hmm_path.save()
#        path_fragment = None
#        p_index = []
#	print sequence[0]
#        for i in range(0, len(sequence[0])):
#	    print sequence[1][i]
#            if i > 0:
#                print sequence[0][i] == sequence[1][i - 1][0]
#            if i > 0 and len(sequence[1][i - 1]) > 1:
#                if path_fragment is not None:
#                    path_fragment.p = ','.join(map(str, p_index))
#                    path_fragment.save()
#                    hmm_path.road.add(path_fragment)
#                    p_index = []
#                if len(sequence[1][i - 1]) > 2:
#                    for j in range(1, len(sequence[1][i - 1]) - 1):
#                        next_road = road_network.roads.get(id=sequence[1][i - 1][j])
#                        path_fragment = PathFragment(road=next_road)
#                        path_fragment.save()
#                        hmm_path.road.add(path_fragment)
#                next_road = road_network.roads.get(id=sequence[0][i])
#                path_fragment = PathFragment(road=next_road)
#                path_fragment.save()
#                prev_id = sequence[0][i]
#            p_index.append(i)
#        hmm_path.save()
#        return {'path': hmm_path, 'mm_prob': self.map_matching_prob, 'bf_prob': self.brute_force_prob}
